import time
import _thread as thread
from collections import defaultdict
from basicFunctions import degasing, openValves, closeValves, pumping

"""
def order_actions (set_actions):

    event_list = defaultdict(list)

    for _name, _params in set_actions.items():
        t_begin=_params['start']
        t_stop=_params['start'] + (_params['minutes']*60+_params['seconds'])

        event_list(t_begin).append(_name, 'start')
        event_list(t_stop).append(_name, 'finish')

    time_points = event_list.keys().sort()

    for t in time_points:
        ordered_list.append((t, event_list[t]))

    return ordered_list
"""

def main_process(set_actions):

    print('You are in main process!')

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error")

    """
    time_init = time.time()
    list_finish_time = []
    # main loop

    #degasing
    lock1=thread.allocate_lock()
    lock1.acquire()
    t1=thread.start_new_thread(degasing,(lock1,))
    
    ordered_list = order_actions(set_actions)

    for local_action in set_actions:

        active_locks = []

        time_current = time.time() - time_init
        print("It is {}".format(time_current))


        # Trigger les events
        # TODO: pas print, use LOGGER
        for event_action_name in list_events_to_trig:
            if set_actions[event_action_name]['type'] == 'PUMP':
                print ('{} Je call PUMP'.format(time_current))
                lock2 = thread.allocate_lock()
                lock2.acquire()
                active_locks.append(lock2)
                thread.start_new_thread(pumping,(0.2, lock2))

            elif set_actions[event_action_name]['type'] == 'VALVE_ACTION' and set_actions[event_action_name]['valve option'] == 'OPENING':
                print ('{} Je call VALVE_OPENING'.format(time_current))
                openValves(set_actions[event_action_name]['valve number'])
            elif set_actions[event_action_name]['type'] == 'VALVE_ACTION' and set_actions[event_action_name]['valve option'] == 'CLOSING':
                print ('{} Je call VALVE_CLOSING'.format(time_current))
                closeValves(set_actions[event_action_name]['valve number'])
            else:
                print ('{} Unknown action'.format(time_current))

            del set_actions[event_action_name]

        for i, (event_to_finish_t_stop, event_to_finish_name) in enumerate(list_finish_time):
            if event_to_finish_t_stop < time_current:
                if set_actions[event_action_name]['type'] == 'PUMP':
                    for lock in active_locks:
                        lock.release()
                    print('{} event finished !'.format(event_to_finish_name))
                else:
                    pass

                del list_finish_time[i]

        time.sleep(1)

        """

    while set_actions != {} or len(list_finish_time) > 0:

        active_locks = []

        time_current = time.time() - time_init
        print("It is {}".format(time_current))

        # Check les events a trigger
        list_events_to_trig = []
        for _name, _params in set_actions.items():
            if _params['start'] <= time_current:
                list_events_to_trig.append(_name)
                list_finish_time.append((_params['start'] + (_params['minutes']* \
                                        60+_params['seconds']), _name))

        # Trigger les events
        # TODO: pas print, use LOGGER
        for event_action_name in list_events_to_trig:

            saea = set_actions[event_action_name]
            print('event action parameters', saea['type'], \
                saea['start'], (saea['minutes']*60 + saea['seconds']))

            if set_actions[event_action_name]['type'] == 'PUMP' and \
                time_current <= (set_actions[event_action_name]['start'] + \
                 (set_actions[event_action_name]['minutes']*60) + \
                 set_actions[event_action_name]['seconds']): # and time.current,time start + duration
                print ('{} Je call PUMP'.format(time_current))
                lock2 = thread.allocate_lock()
                lock2.acquire()
                active_locks.append(lock2)
                thread.start_new_thread(pumping,(0.2, lock2))

            elif set_actions[event_action_name]['type'] == 'PUMP' and \
                time_current > (set_actions[event_action_name]['start'] + \
                 (set_actions[event_action_name]['minutes']*60) + \
                 set_actions[event_action_name]['seconds']): #if past duration --> stop
                print('pumping to be stopped')
                for lock in active_locks:
                    lock.release()

            elif set_actions[event_action_name]['type'] == 'VALVE_ACTION' and set_actions[event_action_name]['valve option'] == 'OPENING':
                print ('{} Je call VALVE_OPENING'.format(time_current))
                openValves(set_actions[event_action_name]['valve number'])

            elif set_actions[event_action_name]['type'] == 'VALVE_ACTION' and set_actions[event_action_name]['valve option'] == 'CLOSING':
                print ('{} Je call VALVE_CLOSING'.format(time_current))
                closeValves(set_actions[event_action_name]['valve number'])
            else:
                print ('{} Unknown action'.format(time_current))

            del set_actions[event_action_name]

        for i, (event_to_finish_t_stop, event_to_finish_name) in enumerate(list_finish_time):
            if event_to_finish_t_stop < time_current:
                    print('{} event finished !'.format(event_to_finish_name))
            else:
                pass

            del list_finish_time[i]

        time.sleep(1)

    print ('{} I am done'.format(time.time() - time_init))
    lock1.release()
