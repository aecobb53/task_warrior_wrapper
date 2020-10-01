import datetime
import json


class ShiftManager:


  def __init__(self):
    self.week = {
      'days':{
        'Mon':{'active':True,  'start':'06:00M', 'end':'13:00M', 'shift_diff':None, 'augment':None},
        'Tue':{'active':True,  'start':'06:00M', 'end':'13:00M', 'shift_diff':None, 'augment':None},
        'Wed':{'active':True,  'start':'06:00M', 'end':'13:00M', 'shift_diff':None, 'augment':None},
        'Thu':{'active':True,  'start':'06:00M', 'end':'13:00M', 'shift_diff':None, 'augment':None},
        'Fri':{'active':True,  'start':'06:00M', 'end':'13:00M', 'shift_diff':None, 'augment':None},
        'Sat':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Sun':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        },
      'swings_start':{
        'Mon':{'active':True,  'start':'13:00M', 'end':'21:00M', 'shift_diff':None, 'augment':None},
        'Tue':{'active':True,  'start':'13:00M', 'end':'21:00M', 'shift_diff':None, 'augment':None},
        'Wed':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Thu':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Fri':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Sat':{'active':True,  'start':'18:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Sun':{'active':True,  'start':'18:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        },
      'swings_end':{
        'Mon':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Tue':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Wed':{'active':True,  'start':'13:00M', 'end':'21:00M', 'shift_diff':None, 'augment':None},
        'Thu':{'active':True,  'start':'13:00M', 'end':'21:00M', 'shift_diff':None, 'augment':None},
        'Fri':{'active':True,  'start':'13:00M', 'end':'21:00M', 'shift_diff':None, 'augment':None},
        'Sat':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Sun':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        },
      'mids':{
        'Mon':{'active':True,  'start':'21:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Tue':{'active':True,  'start':'21:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Wed':{'active':True,  'start':'21:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Thu':{'active':True,  'start':'21:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Fri':{'active':True,  'start':'21:00M', 'end':'06:00M', 'shift_diff':None, 'augment':None},
        'Sat':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        'Sun':{'active':False, 'start':'00:00M', 'end':'00:00M', 'shift_diff':None, 'augment':None},
        },
      }
    self.start_week = 29
    self.start_week_schedule = {
      'Eric':'swings_end',
      'Justin':'swings_start',
      'Andrew':'mids',
      'Chris':'days',
      'Zak':None,
      'Adam':None,
      }
    self.shift_order = (
      'days',
      'swings_start',
      'mids',
      'swings_end',
      )
    with open('shift_manager.json') as jf:
      self.config = json.load(jf)


  def shift_rotation(self, week, start_week=None):

    if start_week == None:
      start_week = self.config['start_week']

    if not isinstance(week, int):
      week = int(week)

    rotate_count = week - start_week
    if rotate_count < 0:
      rotate_count = week - (start_week - 52)

    if rotate_count < 0:
      raise ValueError('The current week is before the set week. Please reset the start_week')

    workers = [w for w in self.config['start_week_schedule'].keys() if self.config['start_week_schedule'][w] != None]
    shift_list = []

    for shift in self.config['shift_order']:
      shift_list.append([k for k,v in self.config['start_week_schedule'].items() if v == shift][0])

    for i in range(0,rotate_count):
      shift_list.insert(0, shift_list.pop())
  
    shifts = {k:v for v,k in zip(shift_list, self.config['shift_order'])}
    return shifts


  def shift_check(self, time_obj):
    week_n = datetime.datetime.strftime(time_obj, "%U")
    day = datetime.datetime.strftime(time_obj, "%a")
    time = int(datetime.datetime.strftime(time_obj, "%H"))
    week_shifts = self.shift_rotation(week_n)
    shifts = {}
    for shift, schedule in self.config['week'].items():
      if not schedule[day]['active']:
        continue
      start = int(schedule[day]['start'][:2])
      end = int(schedule[day]['end'][:2])
      if start > end:
        end += 24
      if  start <= time and time < end:
        current_shift = {
          'week':week_n, 
          'day': day, 
          'shift': shift, 
          'worker':week_shifts[shift],
          'shift_start': schedule[day]['start'],
          'shift_end': schedule[day]['end'],
          }
        return current_shift
    if  start >= time and time < end:
      current_shift = {
        'week':week_n, 
        'day': day, 
        'shift': shift, 
        'worker':week_shifts[shift],
        'shift_start': schedule[day]['start'],
        'shift_end': schedule[day]['end'],
        }
      return current_shift
    current_shift = {
      'week':week_n, 
      'day': day, 
      'shift': 'on-call', 
      'worker':week_shifts['days'],
      }
    return current_shift

  def on_now(self):
    return self.shift_check(datetime.datetime.now())


  def user_check(self, user, time_check=datetime.datetime.utcnow()):
    on_shift = self.shift_check(time_check)
    if on_shift['worker'].upper() == user.upper():
      return True
    return False


  def print_json(self):
    print(json.dumps(self.__dict__, indent = 2))


# now = datetime.datetime.now()
# sm = ShiftManager()
# # sm.print_json()

# # This is in the time of the computer right now!!
# print(sm.shift_check(now))
# testtime = datetime.datetime.strptime('2020-09-27T10:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# print(sm.shift_check(testtime))
# testtime = datetime.datetime.strptime('2020-09-30T10:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# print(sm.shift_check(testtime))
# print(sm.on_now())

# print(f"Setup for waking up before shift")
# now = datetime.datetime.strptime('2020-08-11T15:00:00Z', '%Y-%m-%dT%H:%M:%SZ')




# # print(sm.shift_check(now))
# # testtime = datetime.datetime.strptime('2020-07-20T14:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# # print(sm.shift_check(testtime))
# # testtime = datetime.datetime.strptime('2020-07-20T21:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# # print(sm.shift_check(testtime))
# # testtime = datetime.datetime.strptime('2020-07-21T03:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# # print(sm.shift_check(testtime))
# # testtime = datetime.datetime.strptime('2020-07-23T21:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# # print(sm.shift_check(testtime))
# # testtime = datetime.datetime.strptime('2020-07-19T17:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
# # print(sm.shift_check(testtime))
# print(sm.user_check('Andrew'))
