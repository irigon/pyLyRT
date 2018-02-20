import sqlite3
import inspect
import sys
import importlib
import hashlib
import _pickle as pickle
#import json
import libs


db_args = "CompartmentId text CHECK(TYPEOF(CompartmentId) = 'text'), " \
               "CorePlayerId text CHECK(TYPEOF(CorePlayerId) = 'text'), " \
               "PlayerId text CHECK(TYPEOF(PlayerId) = 'text'), " \
               "RoleId text CHECK(TYPEOF(RoleId) = 'text'), " \
               "RelationType text CHECK(TYPEOF(RelationType) = 'text'), " \
               "BindingLevel integer CHECK(TYPEOF(BindingLevel) = 'integer'), " \
               "BindingSequence integer CHECK(TYPEOF(BindingSequence) = 'integer')"


class Reg:
    def __init__(self, table_name):
        self.conn = sqlite3.connect(":memory:")
        self.name = table_name
        self.conn.execute("CREATE TABLE " + self.name + " (" + db_args + ")")
        self.conn.execute('CREATE INDEX search_order ON ' + self.name + ' \
                            (BindingLevel DESC, BindingSequence DESC)')
        self.obj_dict = {}

    def __del__(self):
        self.conn.close()

    def roles_player_by(self, compartment_name):
        pass

    def players_that_play(self, roleuuid, compartment=None):
        players=self.conn.execute("SELECT CorePlayerId FROM {} WHERE RoleId='{}')".format(\
                            self.name, roleuuid))
        return players

    def add_relation(self, compartmentId, coreId, playerId, roleId, relationType, level, sequence):
        self.conn.execute("INSERT INTO {} VALUES('{}', '{}', '{}' , '{}', '{}', {}, {})".format(\
                            self.name, compartmentId, coreId, playerId, roleId, relationType, level, sequence))


    #TODO: might be a object in two compartments concurrently or is this exclusive
    def find_next_level_and_sequence(self, core, player, role, type):
        # line is 1, but number is 1+max level for this player
        if type=='PPR':
            level = 1  # in a player plays role, core and player are the same, and the distance to the role is 1
            result = self.conn.execute("SELECT BindingSequence FROM {} WHERE CorePlayerId='{}' and PlayerId='{}' \
                                              order by BindingLevel DESC,BindingSequence DESC".format \
                                             (self.name, core, player)).fetchall()

        elif type=='RPR':   # find out the level of the role
            result = self.conn.execute("SELECT BindingLevel FROM {} WHERE CorePlayerId='{}' and RoleId='{}' \
                                              order by BindingLevel DESC".format \
                                             (self.name, core, player)).fetchall()
            try:
                level = result[0][0] + 1
            except:
                print('No core player {} with roleId {} found. Is this a RPR relation?'.format(core, player))
                raise
            # the len of result will not be 0, since for a player play a role, it urges a player to play it first
            result = self.conn.execute("SELECT BindingSequence FROM {} WHERE CorePlayerId='{}' and BindingLevel='{}' \
                                              order by BindingLevel DESC,BindingSequence DESC".format \
                                             (self.name, core, level)).fetchall()
        try:
            sequence = 1 if len(result) == 0 else result[0][0]+1
        except IndexError:
            print('Core player found at bind level {}')
            raise

        return (level, sequence)

    # TODO: when creating a player, it must have a attribute name
    # TODO: when creating a core, it must have a dictionary of players
    def bind(self, compartment, core, player, role, relationType):
        newIdx = self.find_next_level_and_sequence(core.uuid, player.uuid, role.uuid, relationType)
        self.add_relation(compartment.uuid, core.uuid, player.uuid, role.uuid, relationType, newIdx[0], newIdx[1])

        # at the end, who will need the pointer to the role is the core object (player or compartment)
        # the role plays role explicits the context from which the call will be done, through levels and sequences,
        # but when a core calls a method, we will find the role that should call this method and this instance should
        # be called. Putting this role bound to the core through its uuid allows us to call it directly, as soon
        # as the context that should call the method is found.
        core.roles[role.uuid]=role
        if role.uuid not in libs.g.roles_played_by:
            libs.g.roles_played_by[role.uuid]=[]
        libs.g.roles_played_by[role.uuid].append(core)


    # we probably have to consider a core can not run the same context concurrently in two different contexts (RPR)

    #   finds the line with the core and role (either a PPR or RPR)
    #       verify that it is only one, or throw an exception (it should be just one)
    #   create a queue with role played
    #   while queue is not empty:
    #       head = dequeue() // remove the line from DB and hold the line
    #       enqueue all roles played by this 'head' (DB for lines with the core 'core' and player 'dequeued role')
    #       gets the core of the line and delete the 'head' from its dictionary

    # the index must not be updated, since the search always get the largest one, never inserting on the middle
    def unbind(self, core_id, role_id):
        # erases the roleId as role, independent if it is PPR or PRP
        result = self.conn.execute("DELETE FROM {} WHERE CorePlayerId='{}' and RoleId='{}'". \
                                   format(self.name, core_id, role_id))
        queue=[role_id]
        while len(queue) > 0:
            role=queue.pop()
            result = self.conn.execute("SELECT * FROM {} WHERE CorePlayerId='{}' and PlayerId='{}'". \
                                       format(self.name, core_id, role)).fetchall()
            queue.extend([x[3] for x in result])
            result = self.conn.execute("DELETE FROM {} WHERE CorePlayerId='{}' and PlayerId='{}'". \
                                       format(self.name, core_id, role))
            #g.players[core_id].roles.pop(role, None)



    def invokeRole(self, compartment, core, method):
        ordered_list = self.conn.execute("SELECT * FROM {} WHERE CompartmentId='{}' and CorePlayerId='{}' \
                                                order by BindingLevel DESC,BindingSequence DESC".\
                                               format(self.name, compartment.uuid, core.uuid)).fetchall()
        # verify if this method exists in any of the contexts found
        ret = None
        for binding_row in ordered_list:
            if hasattr(core.roles[binding_row[3]], method):
                ret = core.roles[binding_row[3]]
                break

        if ret == None:
            ret = core

        # otherwise, try to run in the core
        return getattr(ret, method)()

    # nspace.roles stores the digest of the class of a role
    # this is necessary, since inotify migh cause duplicated events for the same signal (WRITE_CLOSE)
    # a duplicated update of a class would update twice every instance
    # If the update is related to the last (say the Developer received 100+lastSalary), this would
    # two updates would result in the developer receiving lastSalary+2*100

    # https://askubuntu.com/questions/710422/why-do-inotify-events-fire-more-than-once
    # the solution was to calculate a class signature from a md5 digest and store in the nspace['role_name']
    # Before a new role be updated, if calculates the digest of signature and see if an update is needed.
    # An update of a class with no changes will be then ignored.

    def add_module(self, module_name):
        pkg=None
        try:
            if module_name in sys.modules:
                pkg = importlib.reload(sys.modules[module_name])
            else:
                pkg = importlib.import_module(module_name)
        except Exception as ex:
            print('Module could not be imported, {}'.format(ex))
            pkg = None

        if pkg is not None:
            classes = [getattr(pkg, name) for name in dir(pkg)
                       if inspect.isclass(getattr(pkg, name))]
            for c in classes:
                # inotify can cause duplicated events
                duplicated = self.add_role(c)
                if not duplicated:
                    # if this role is being played by some core, update the core.
                    if c.classtype in libs.g.roles_played_by:
                        for core in libs.g.roles_played_by[c.classtype]:
                            core.roles[c.classtype] = c(instance=core.roles[c.classtype])

    def add_role(self, role):
        if not inspect.isclass(role):
            raise AttributeError

        serialized_new=pickle.dumps(role, 2.3)
        newclass_digest = hashlib.md5(serialized_new).digest()
        print('Adding role {}, md5: {}'.format(role.classtype, newclass_digest))
        if role.classtype in libs.g.nspace:
            serialized_old = libs.g.nspace[role.classtype][1]
            print("{}: hash old: {}, hash new: {}".format(role.classtype, serialized_old, newclass_digest))
            if  serialized_old == newclass_digest:
                print('duplicated: {}, {}, {}'.format(libs.g.nspace[role.classtype][0], role, libs.g.nspace[role.classtype]==role))
                return True # new class is duplicated and will be ignored
        else:
            print('class nova... calma')
        libs.g.nspace[role.classtype]=[role, newclass_digest]
        print('hash old: {}'.format(libs.g.nspace[role.classtype]))
        return False
