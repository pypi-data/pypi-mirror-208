'''
class to Interface between json <=> python dict<tuple<int, int, int, int>, float> <=> cpp map<OmegaPoint, double>
json file contains omega integrals computed for a mie-potential without BH-diameters.

Note:
    The database will only contain a mixture once. That is: AR,HE and HE,AR is the same entry. Internal functions
    ensure that the correct values are returned. So if OmegaDb is initialized with (HE,AR) and (AR,HE) is found in the
    database, the components will be inverted.

The class is written such that only a single instance of the database-object can read/write from the database file
at any given time (accross multiple processes). Whenever an object wants to read/write, it moves the database to a
name-mangled file, does whatever it wants to do, then moves the file back. If the database file does not exist, that
means some other instance is working on it, and it waits until the file is available before grabbing it.
Note that this can lead to an infinite waiting loop if some instance crashes while working on the file.
'''

import json, os, shutil, time

DB_PATH = os.path.dirname(__file__) + '/collision_integrals/'


class OmegaDb:
    '''
    self._db mirrors the database entry for the current mixture. If the mixture is either 'X,Y' or 'Y,X',
    self._db will be the dict corresponding exactly to the entry found in the database file
    '''
    def __init__(self, comps, potential, parameter_ref):
        # Unique name for this instance. Using time in case some magic happens and two instances have the same address.
        # See grab_db() and release_db() for usage
        self.mangler = str(id(self) + time.time_ns())

        self.__true_comps = comps # This is the mixture for which entries will be returned
        self._flipped_comps = False
        self._db = {} # Will contain k, v pairs with k corresponding to the key being used by the database

        c1, c2 = self._db_mix.split(',')

        self.__c1_db_path = DB_PATH + c1 + '.json'
        self.__c2_db_path = DB_PATH + c2 + '.json'

        if ','.join((c1, c2)) + '.json' in os.listdir(DB_PATH):
            self.__mix_db_path = DB_PATH + ','.join((c1, c2)) + '.json'
        elif ','.join((c2, c1)) + '.json'  in os.listdir(DB_PATH):
            self.__mix_db_path = DB_PATH + ','.join((c2, c1)) + '.json'
            self._flipped_comps = True
        else:
            self.__mix_db_path = DB_PATH + ','.join((c1, c2)) + '.json'

        self.grab_db(self.__c1_db_path)
        self.__c1_db = json.load(self.mangler + self.__c1_db_path)
        self.release_db(self.__c1_db_path)
        self.grab_db(self.__c2_db_path)
        self.__c2_db = json.load(self.mangler + self.__c1_db_path)
        self.release_db(self.__c2_db_path)
        self.grab_db(self.__mix_db_path)
        self.__mix_db = json.load(self.mangler + self.__c1_db_path)
        self.release_db(self.__mix_db_path)

        for k, v in self.__c1_db.items():
            k = (1, k[0], k[1], k[2])
            self._db[k] = v
        for k, v in self.__c2_db.items():
            k = (2, k[0], k[1], k[2])
            self._db[k] = v
        for k, v in self.__mix_db.items():
            self._db[k] = v

        self._updated = False # Keep track of whether new computations have been entered into the database

    def grab_db(self, path):
        # Move the database to a file that is unique to this object instance
        # This ensures that only one instance can read/write at a time
        while True:
            try:
                shutil.move(path, path + self.mangler)
                break
            except FileNotFoundError:
                time.sleep(0.01)

    def release_db(self, path): # Move the database back to the common path, so that other instances can access it
        shutil.move(path + self.mangler, path)

    def get_db_key(self, op_key):
        # Take key as an OmegaPoint (used on cpp-side), return database key as a str.
        # If components are flipped, flip the key before returning
        # The return value is the correct database key.
        db_key = (op_key.ij, op_key.l, op_key.r, op_key.T_dK)
        if self._flipped_comps is True:
            if db_key[0] == 1:
                db_key = (2, db_key[1], db_key[2], db_key[3])
            elif db_key[0] == 2:
                db_key = (1, db_key[1], db_key[2], db_key[3])
            return str(db_key)

        return str(db_key)

    def get_return_key(self, db_key):
        # Take database key as a string, return tuple.
        # If components are flipped, flip the key before returning
        # The return value is the key corresponding to the mixture self.__true_comps
        key = tuple(int(i) for i in db_key.strip('()').split(','))
        if self._flipped_comps is True:
            if key[0] == 1:
                key = (2, key[1], key[2], key[3])
            elif key[0] == 2:
                key = (1, key[1], key[2], key[3])
            return key

        return key

    def db_to_vectors(self):
        # Return a (N, 4) and a (N, ) list of points and corresponding values
        pairs = [[self.get_return_key(db_k), v] for db_k, v in self._db.items()]
        vals = [p[1] for p in pairs]
        points = [[i for i in p[0]] for p in pairs] # (ij, l, r, T_dK)
        return points, vals

    def update(self, map):
        # map is the KineticGas.omega_map<OmegaPoint, double>
        for k, v in map.items():
            self._db[self.get_db_key(k)] = v
        self._updated = True

    def pull_updates(self):
        with open(self.__c1_db_path + self.mangler, 'r') as file:
            db = json.load(file)
        try:
            comp_db = db[self._db_mix]
        except KeyError:
            comp_db = {}
        for k, v in comp_db.items():
            self._db[k] = v

    def dump(self):
        if self._updated is True: # Only touch db if this instance has been updated
            self.grab_db(self.__c1_db_path)
            self.pull_updates() # Pull before pushing (in case another instance has written new computations to the database)
            with open(self.working_db_path, 'r') as file:
                full_db = json.load(file)

            for k, v in self._db.items():
                if self._db_mix in full_db.keys():
                    full_db[self._db_mix][k] = v
                else:
                    full_db[self._db_mix] = {k : v}

            with open(self.working_db_path, 'w') as file:
                json.dump(full_db, file, indent=6)

            self.release_db()

    def table(self, thing):
        return str(thing) + ' '*(25 - len(str(thing)))

    def __repr__(self):
        r = 'Omega values for mixture ' + self.__true_comps + ', using database entry for ' + self._db_mix + '\n'
        r += self.table('Database key') + self.table('Return key') + '\t\t Value\n\n'
        for k, v in self._db.items():
            r += self.table(k) + self.table(self.get_return_key(k)) + '\t'+ str(v) + '\n'

        return r