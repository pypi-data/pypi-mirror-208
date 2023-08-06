#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is an example of working with very large data. There are about
700,000 unduplicated donors in this database of Illinois political
campaign contributions.

With such a large set of input data, we cannot store all the comparisons
we need to make in memory. Instead, we will read the pairs on demand
from the PostgresSQL database.

__Note:__ You will need to run `python pgsql_big_dedupe_example_init_db.py`
before running this script.

For smaller datasets (<10,000), see our
[csv_example](http://datamade.github.io/dedupe-examples/docs/csv_example.html)
"""
import os
import time
import logging
import optparse
import locale
import itertools
import io
import csv

import dj_database_url
import psycopg2.extras

import dedupe
import numpy


from psycopg2.extensions import register_adapter, AsIs
from dedupe.datamodel import VARIABLE_CLASSES
from dedupe.variables.base import FieldType as FieldVariable
from collections import defaultdict

register_adapter(numpy.int32, AsIs)
register_adapter(numpy.int64, AsIs)
register_adapter(numpy.float32, AsIs)
register_adapter(numpy.float64, AsIs)


class Readable(object):

    def __init__(self, iterator):

        self.output = io.StringIO()
        self.writer = csv.writer(self.output)
        self.iterator = iterator

    def read(self, size):

        self.writer.writerows(itertools.islice(self.iterator, size))

        chunk = self.output.getvalue()
        self.output.seek(0)
        self.output.truncate(0)

        return chunk


class CustomModelParam:
    ACCURACY = "accuracy"
    APPROXIMATE = "approximate"
    EXACT = "exact"
    SIMPLE_PREDICATE = "SimplePredicate"
    WHOLE_FIELD_PREDICATE = "wholeFieldPredicate"
    TFIDF = "TfidfTextSearch"
    THRESH_HOLD = "threshold"
    FIELD = "field"
    IS_ARRAY = "is_array"


class CustomModel:

    @staticmethod
    def typify_variables(variable_definitions):
        primary_variables = []
        for definition in variable_definitions:
            variable_class = VARIABLE_CLASSES[definition.get('type')]
            variable_object: object = variable_class(definition)
            assert isinstance(variable_object, FieldVariable)
            primary_variables.append(variable_object)
        return primary_variables

    @staticmethod
    def get_all_predicates(primary_variables):
        all_predicates = set()
        for var in primary_variables:
            for p in var.predicates:
                all_predicates.add(p)
        return all_predicates

    @staticmethod
    def chose_algorithm(all_predicates, variable_definitions):
        """
            wholeFieldPredicate: Exact
        """
        algorithm_exact = []
        algorithm_approximate = []
        for definition in variable_definitions:
            for predicates in all_predicates:
                if definition.get(CustomModelParam.FIELD) not in predicates.__name__:
                    continue
                if definition.get(CustomModelParam.ACCURACY) == CustomModelParam.APPROXIMATE and \
                        CustomModelParam.TFIDF in predicates.type and predicates.threshold == 0.8:
                    predicates.threshold = definition.get(CustomModelParam.THRESH_HOLD)
                    predicates.__name__ = '({}, {})'.format(definition.get(CustomModelParam.THRESH_HOLD),
                                                            definition.get(CustomModelParam.FIELD))
                    if definition.get(CustomModelParam.IS_ARRAY):
                        predicates.is_array = True
                    algorithm_approximate.append(predicates)
                    algorithm_exact.append(predicates)
                elif definition.get(CustomModelParam.ACCURACY) == CustomModelParam.EXACT and \
                        predicates.type == CustomModelParam.SIMPLE_PREDICATE and \
                        CustomModelParam.WHOLE_FIELD_PREDICATE in predicates.__name__:
                    if definition.get(CustomModelParam.IS_ARRAY):
                        predicates.is_array = True
                    algorithm_exact.append(predicates)
        return algorithm_exact, algorithm_approximate

    @staticmethod
    def index_list():
        return defaultdict(list)

    @staticmethod
    def set_index_field(algorithm_approximate):
        index_fields = defaultdict(CustomModel.index_list)
        for full_predicate in algorithm_approximate:
            for predicate in full_predicate:
                if hasattr(predicate, "index"):
                    index_fields[predicate.field][predicate.type].append(predicate)
        return index_fields


def record_pairs(result_set):

    for i, row in enumerate(result_set):
        a_record_id, a_record, b_record_id, b_record = row
        record_a = (a_record_id, a_record)
        record_b = (b_record_id, b_record)

        yield record_a, record_b

        if i % 10000 == 0:
            print(i)


def cluster_ids(clustered_dupes):

    for cluster, scores in clustered_dupes:
        cluster_id = cluster[0]
        for donor_id, score in zip(cluster, scores):
            if donor_id in [127, 598, 148]:
                a = 1
            print(donor_id, cluster_id, score)
            yield donor_id, cluster_id, score


if __name__ == '__main__':
    # ## Logging

    # Dedupe uses Python logging to show or suppress verbose output. Added
    # for convenience.  To enable verbose output, run `python
    # pgsql_big_dedupe_example.py -v`
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help='Increase verbosity (specify multiple times for more)'
                    )
    (opts, args) = optp.parse_args()
    log_level = logging.WARNING
    if opts.verbose:
        if opts.verbose == 1:
            log_level = logging.INFO
        elif opts.verbose >= 2:
            log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)

    # ## Setup
    settings_file = 'pgsql_big_dedupe_example_settings'
    training_file = 'pgsql_big_dedupe_example_training.json'

    start_time = time.time()

    # Set the database connection from environment variable using
    # [dj_database_url](https://github.com/kennethreitz/dj-database-url)
    # For example:
    #   export DATABASE_URL=postgres://user:password@host/mydatabase
    DATABASE_URL = "postgresql://hoanglcm:13456@localhost:5432/campfin"

    db_conf = dj_database_url.config(default=DATABASE_URL)

    if not db_conf:
        raise Exception(
            'set DATABASE_URL environment variable with your connection, e.g. '
            'export DATABASE_URL=postgres://user:password@host/mydatabase'
        )

    read_con = psycopg2.connect(database=db_conf['NAME'],
                                user=db_conf['USER'],
                                password=db_conf['PASSWORD'],
                                host=db_conf['HOST'],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    write_con = psycopg2.connect(database=db_conf['NAME'],
                                 user=db_conf['USER'],
                                 password=db_conf['PASSWORD'],
                                 host=db_conf['HOST'])

    # We'll be using variations on this following select statement to pull
    # in campaign donor info.
    #
    # We did a fair amount of preprocessing of the fields in
    # `pgsql_big_dedupe_example_init_db.py`

    DONOR_SELECT = "SELECT donor_id, city, name, zip, state, address " \
                   "from processed_donors"

    # DONOR_SELECT = "select * from processed_donors where donor_id in (SELECT donor_id FROM processed_donors limit 1000) order by address"

    # ## Training

    if os.path.exists(settings_file):
        print('reading from ', settings_file)
        with open(settings_file, 'rb') as sf:
            deduper = dedupe.StaticDedupe(sf, num_cores=4)
    else:

        # Define the fields dedupe will pay attention to
        #
        # The address, city, and zip fields are often missing, so we'll
        # tell dedupe that, and we'll learn a model that take that into
        # account
        fields = [{'field': 'name', 'type': 'String'},
                  {'field': 'address', 'type': 'String',
                   'has missing': True},
                  {'field': 'city', 'type': 'ShortString', 'has missing': True},
                  {'field': 'state', 'type': 'ShortString', 'has missing': True},
                  {'field': 'zip', 'type': 'ShortString', 'has missing': True},
                  ]

        # Create a new deduper object and pass our data model to it.
        deduper = dedupe.Dedupe(fields, num_cores=4)

        # Named cursor runs server side with psycopg2
        with read_con.cursor('donor_select') as cur:
            cur.execute(DONOR_SELECT)
            temp_d = {i: row for i, row in enumerate(cur)}

        # If we have training data saved from a previous run of dedupe,
        # look for it an load it in.
        #
        # __Note:__ if you want to train from
        # scratch, delete the training_file
        if os.path.exists(training_file):
            print('reading labeled examples from ', training_file)
            with open(training_file) as tf:
                deduper.prepare_training(temp_d, tf)
        else:
            deduper.prepare_training(temp_d)

        del temp_d

        # ## Active learning

        print('starting active labeling...')
        # Starts the training loop. Dedupe will find the next pair of records
        # it is least certain about and ask you to label them as duplicates
        # or not.

        # use 'y', 'n' and 'u' keys to flag duplicates
        # press 'f' when you are finished
        dedupe.console_label(deduper)
        # When finished, save our labeled, training pairs to disk
        with open(training_file, 'w') as tf:
            deduper.write_training(tf)

        # Notice our argument here
        #
        # `recall` is the proportion of true dupes pairs that the learned
        # rules must cover. You may want to reduce this if your are making
        # too many blocks and too many comparisons.
        deduper.train(recall=0.90)

        with open(settings_file, 'wb') as sf:
            deduper.write_settings(sf)

        # We can now remove some of the memory hogging objects we used
        # for training
        deduper.cleanup_training()
    custom = True
    if custom:
        variable_definitions = [
            {'field': 'address', 'type': 'String', 'accuracy': 'approximate', 'threshold': 0.7, "is_array": True},
            {'field': 'name', 'type': 'String', 'accuracy': 'approximate', 'threshold': 0.7}
        ]
        primary_variables = CustomModel.typify_variables(variable_definitions=variable_definitions)
        all_predicates = CustomModel.get_all_predicates(primary_variables=primary_variables)
        algorithm, algorithm_approximate = CustomModel.chose_algorithm(
            all_predicates=all_predicates, variable_definitions=variable_definitions
        )
        index_fields = CustomModel.set_index_field(algorithm_approximate=algorithm_approximate)
        deduper.fingerprinter.index_fields = index_fields
        print("debug", algorithm)
        print("debug with set", set(algorithm))
        print("debug with list set", list(set(algorithm)))
        deduper.fingerprinter.predicates = algorithm

    # ## Blocking
    print('blocking...')

    # To run blocking on such a large set of data, we create a separate table
    # that contains blocking keys and record ids
    print('creating blocking_map database')
    with write_con:
        with write_con.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS blocking_map")
            cur.execute("CREATE TABLE blocking_map "
                        "(block_key text, donor_id INTEGER)")

    # If dedupe learned a Index Predicate, we have to take a pass
    # through the data and create indices.
    print('creating inverted index')

    for field in deduper.fingerprinter.index_fields:
        with read_con.cursor('field_values') as cur:
            cur.execute("SELECT DISTINCT %s FROM processed_donors" % field)
            field_data = (row[field] for row in cur)
            deduper.fingerprinter.index(field_data, field)

    # Now we are ready to write our blocking map table by creating a
    # generator that yields unique `(block_key, donor_id)` tuples.
    print('writing blocking map')

    with read_con.cursor('donor_select') as read_cur:
        read_cur.execute(DONOR_SELECT)

        full_data = ((row['donor_id'], row) for row in read_cur)
        b_data = deduper.fingerprinter(full_data)

        with write_con:
            with write_con.cursor() as write_cur:
                write_cur.copy_expert('COPY blocking_map FROM STDIN WITH CSV',
                                      Readable(b_data),
                                      size=10000)
    # free up memory by removing indices
    deduper.fingerprinter.reset_indices()

    logging.info("indexing block_key")
    with write_con:
        with write_con.cursor() as cur:
            cur.execute("CREATE UNIQUE INDEX ON blocking_map "
                        "(block_key text_pattern_ops, donor_id)")

    # ## Clustering

    with write_con:
        with write_con.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS entity_map")

            print('creating entity_map database')
            cur.execute("CREATE TABLE entity_map "
                        "(donor_id INTEGER, canon_id INTEGER, "
                        " cluster_score FLOAT, PRIMARY KEY(donor_id))")

    print('creating suggest_merge_id database')
    with write_con:
        with write_con.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS suggest_merge_id")
            cur.execute("CREATE TABLE suggest_merge_id "
                        "(left_donor_id INTEGER, right_donor_id INTEGER)")

            cur.execute("insert into suggest_merge_id "
                        "(left_donor_id, right_donor_id) "
                        "(select DISTINCT l.donor_id as left_donor_id, r.donor_id as right_donor_id "
                        "from blocking_map as l "
                        "INNER JOIN blocking_map as r "
                        "using (block_key) "
                        "where l.donor_id < r.donor_id order by l.donor_id)")

    locale.setlocale(locale.LC_ALL, '')  # for pretty printing numbers

    read_con.close()
    write_con.close()

    print('ran in', time.time() - start_time, 'seconds')
