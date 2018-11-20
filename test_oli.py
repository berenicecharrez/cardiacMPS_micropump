import time
import _thread as thread
from collections import defaultdict
from basicFunctions import degasing, openValves, pumping #closeValves
import heapq

"""
Takes a dictionary of actions and creates a minimum heap based on start and
finishing time for each of them.
"""
def order_actions (set_actions):

    h=[]

    for _name, _params in set_actions.items():
        t_begin=_params['start']
        t_finish=_params['start'] + (_params['minutes']*60+_params['seconds'])

        heapq.heappush(h,(t_begin, _name, 'start'))
        heapq.heappush(h, (t_finish, _name, 'finish'))

    return h

def start_pumping (timestep):
    lock = thread.allocate_lock()
    lock.acquire()
    thread.start_new_thread(pumping,(timestep, lock))

    return lock

def opening_valve (valve):
    lock1 = thread.allocate_lock()
    lock1.acquire()
    thread.start_new_thread(openValves,(valve, lock1))

    return lock1
"""
Main process launching Raspberry pie
"""

def main_process(set_actions):

    #status = 0
    print('You are in main process!')

    try:
        import RPi.GPIO as GPIO
    except:
        print("Error")

    # main loop

    time_init = time.time()

    #degasing
    lock2=thread.allocate_lock()
    lock2.acquire()
    t1=thread.start_new_thread(degasing,(lock2,))

    action_heap = order_actions(set_actions)

    while(len(action_heap) > 0):

        current_action = heapq.heappop(action_heap) #get the first item from the heap

        active_locks_pump = []
        active_locks_valves = []

        time_current = time.time() - time_init
        #print("It is {}".format(time_current))

        #for more efficiency: only go through the while loop when an event is going to happen,
        #no need of going through it every msec
        time_difference = max(0, current_action[0] - time_current)
        #print("time", time_current, current_action[0])
        time.sleep(time_difference)

        # Trigger les events
        # TODO: pas print, use LOGGER

        saca = set_actions[current_action[1]]
        #print('event action parameters', saea['type'], saea['start'], (saea['minutes']*60 + saea['seconds']))

        if saca['type'] == 'PUMP':
            if current_action[2] == 'start':
                #print('pumping to be started')
                lock = start_pumping(0.2) #timestep = 0.2
                active_locks_pump.append(lock)

            if current_action[2] == 'finish': #if past duration --> stop
                #print('pumping to be stopped')
                for lock in active_locks_pump:
                    lock.release()

        elif saca['type'] == 'VALVE ACTION':
            if current_action[2] == 'start':# and saca['valve option'] == 'OPENING':
                #print('valve to be opened')
                lock1 = opening_valve(saca['valve number'])
                active_locks_valves.append(lock1)
                print('Valve is opening: {}'.format(saca['valve number']))

            if current_action[2] == 'finish': #or saca['valve option'] == 'CLOSING': if past duration --> stop
                #print('valve to be closed')
                for lock1 in active_locks_valves:
                    lock1.release()
                print('Valve is closed1: {}'.format(saca['valve number']))


            """if saca['valve option'] == 'OPENING':
                print ('{} Je call VALVE_OPENING'.format(time_current))
                openValves(saca['valve number'])
            if saca['valve option'] == 'CLOSING':
                print ('{} Je call VALVE_CLOSING'.format(time_current))
                closeValves(saca['valve number'])
            """

        else:
            print ('{} Unknown action'.format(time_current))

        print(current_action[1], current_action[2])

        #time.sleep(1)

    print ('{} I am done'.format(time.time() - time_init))
    lock2.release()
    time.sleep(5)
    #status = 1

    #return status

"""
       #degasing
    lock1=thread.allocate_lock()
    lock1.acquire()
    t1=thread.start_new_thread(degasing,(lock1,))

    time_init = time.time()
    list_finish_time = []

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
    time.sleep(2)

"""

#    while thread.active_count():
#        pass
#    print('ok done final')
