import os
from ortools.sat.python import cp_model
import json
import sqlite3
from math import gcd
from websocket import create_connection
from shift import Shift

TOTAL_DAY_MINUTES = 1440
TOTAL_DAY_SEGMENTS = 287
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]

        
def main():
    try:
        ws = create_connection('ws://localhost:5555/websocket')
        print("Connected to WebSocket server.")

        scheduler = Scheduler(1)
        scheduler.solve()
        ws.send('schedule_ready')
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ws' in locals():
            ws.close()
    

class Scheduler:
    def __init__(self, team_id):
        self.model = cp_model.CpModel()
        self.team_id = team_id
        self.emps_num = len(self.getEmployeesOfTeam())
        self.init_shifts = []
        self.shifts = []
        self.solver = cp_model.CpSolver()
        self.days = []
        self.shifts_for_day = []
        self.emps_ids = []

    # MAIN SOLVER
    def solve(self):
        for i in ALL_DAYS:
            self.createShiftsForDay(i)
        self.shifts = self.initialize_shifts()
        self.days = self.getAllShiftDays()

        for d in self.days:
            for s in self.getShiftsOfDay(d):
                self.shifts_for_day.append([d, s])

        for e in self.getEmployeesOfTeam():
            self.emps_ids.append(e[0])

        solution_callback = SolutionCallback(self.shifts, self.init_shifts)
        self.apply_constraints()

        self.solver.parameters.enumerate_all_solutions = True
        self.solver.parameters.max_time_in_seconds = 5.0
        self.solver.parameters.random_seed = 1

        self.solver.SearchForAllSolutions(self.model, solution_callback)
        print(f"Done — solutions found: {solution_callback.solution_count}")

        
        

    # CONSTRAINTS
    def apply_constraints(self):
        self.C_personnelNeedPerShift()
        self.C_dailyHoursPerEmployee()
        self.C_lastShiftOfDayFirstShiftOfNext()

    # 1. FOR EVERY SHIFT THE MINIMUM AMOUNT OF EMPLOYEES NEEDED SHOULD BE WORKING
    def C_personnelNeedPerShift(self):
        for d in self.days:
            shifts_of_day = self.getShiftsOfDay(d)
            for s in shifts_of_day:
                vars_for_shift = [self.shifts[(e, d, s)] for e in self.emps_ids]
                emps_needed = None
                for shift in self.init_shifts:
                    if shift.day == d and shift.num == s:
                        emps_needed = shift.emps_need
                        break
                if emps_needed is not None:
                    self.model.Add(sum(vars_for_shift) >= emps_needed)


    # 2. AN EMPLOYEE SHOULD WORK THE EXACT AMOUNT OF TIME AGREED FOR EVERY DAY
    def C_dailyHoursPerEmployee(self):
        minimum_shift = self.calculateMinimumShiftDuration(ALL_DAYS)

        for e in self.emps_ids:
            daily_hours = self.getEmployeeDailyHours(e)
            for d in self.days:
                vars_for_day = []
                shifts_of_day = self.getShiftsOfDay(d)
                for s in shifts_of_day:
                    vars_for_day.append(self.shifts[(e, d, s)])
                if vars_for_day:
                    daily_hours_segs = self.dailyHoursToSegments(daily_hours)
                    self.model.Add(sum(vars_for_day)*minimum_shift == daily_hours_segs)
                else:
                    # Skip constraint if daily_hours is None (employee not found)
                    continue


    # 3. AN EMPLOYEE SHOULD NOT WORK LAST SHIFT OF DAY AND FIRST SHIFT OF THE NEXT DAY
    def C_lastShiftOfDayFirstShiftOfNext(self):
        for e in self.emps_ids:
            first_shifts = []
            last_shifts = []
            for i in range(len(self.days)):
                first_shift = self.getShiftsOfDay(i)[0]
                last_shift = self.getShiftsOfDay(i)[len(self.getShiftsOfDay(i)) - 1]

                if (i == 0): # if its the first day append only the last shift
                    last_shifts.append(self.shifts[(e, self.days[i], last_shift)])

                elif (i == len(self.days) - 1): # if its the last day append only the first shift
                    first_shifts.append(self.shifts[(e, self.days[i], first_shift)])
                
                else:
                    first_shifts.append(self.shifts[(e, self.days[i], first_shift)])
                    last_shifts.append(self.shifts[(e, self.days[i], last_shift)])
            
            # for index i last_shifts[i] is the last shift of the previous day and first_shifts[i] is the first shift of the next
            for i in range(len(first_shifts)):
                vars_for_emp = [first_shifts[i], last_shifts[i]]
                self.model.add_at_most_one(s for s in vars_for_emp)



    # DB FUNCTIONS
    def getDB(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, '..', '..', 'data', 'app-data.db')
            sqliteConnection = sqlite3.connect(db_path)
            return sqliteConnection.cursor()
        except sqlite3.Error as error:
            print('Error occurred -', error)
            sqliteConnection.close()
            return None
    
    def executeQuery(self, query: str):
        try:
            return self.getDB().execute(query).fetchall()
        except sqlite3.Error as error:
            print('Error occurred -', error)
            self.getDB().close()
            return None
        
    def getTeamPersonnelNeedPerSegment(self):
        query = f"SELECT day, segment, emps_needed FROM teams_personnel_need_per_segment WHERE team_id={self.team_id}"
        result = self.executeQuery(query)
        return result

    def getEmployeesOfTeam(self):
        query = f"SELECT * FROM employees WHERE team_id = {self.team_id}"
        result = self.executeQuery(query)
        return result
    
    def getPersonnelNeedForDay(self, day):
        query = f"SELECT segment, emps_needed FROM teams_personnel_need_per_segment WHERE team_id={self.team_id} AND day={day}"
        result = self.executeQuery(query)
        return result

    def getEmployeeDailyHours(self, employee_id):
        query = f"SELECT daily_hours FROM employees WHERE id = {employee_id}"
        result = self.executeQuery(query)
        return result[0][0]
    
    def getMinEmployeesDailyHour(self):
        query = f"SELECT MIN(daily_hours) FROM employees WHERE team_id = {self.team_id}"
        result = self.executeQuery(query)
        return result[0][0]

         
        

    # UTILS

    def dayNumToString(self, day):
        convertion = {
            0: "Δευτέρα",
            1: 'Τρίτη',
            2: 'Τετάρτη',
            3: 'Πέμπτη',
            4: 'Παρασκευή',
            5: 'Σάββατο',
            6: 'Κυριακή'
        }
        return convertion.get(day)
    
    def dayStringToNum(self, day):
        convertion = {
            "Δευτέρα": 0,
            'Τρίτη': 1,
            'Τετάρτη': 2,
            'Πέμπτη': 3,
            'Παρασκευή': 4,
            'Σάββατο': 5,
            'Κυριακή': 6
        }
        return convertion.get(day)

    # from daily_hour (e.g. 8) it translates it into 5-minute segments (e.g. 96)
    def dailyHoursToSegments(self, hours) -> int:
        return int(hours * 12)


    # from 5-minute time segment (e.g. 50) it translates it to real life time format (e.g. 04:10)
    def segmentToStringFormat(self, segment) -> str:
        hours = (segment * 5) // 60
        minutes = (segment * 5) % 60
        hours_str = "0" + str(hours) if hours < 10 else str(hours)
        minutes_str = "0" + str(minutes) if minutes < 10 else str(minutes)
        return hours_str + ":" + minutes_str
    
    # returns a list containing the starting hour (segment) of every day for a specific team
    # based of personnel requirements from the DB
    def findDailyStartingHour(self):
        min_segments = []
        for i in range(7):
            min_segments.append(self.executeQuery(f"SELECT MIN(segment) FROM teams_personnel_need_per_segment WHERE emps_needed > 0 AND day = {i} AND team_id = {self.team_id}")[0][0])
        return min_segments
    

    # similar to the previous function but returns the ending hour
    def findDailyEndingHour(self):
        max_segments = []
        for i in range(7):
            max_segment = self.executeQuery(f"SELECT MAX(segment) FROM teams_personnel_need_per_segment WHERE emps_needed > 0 AND day = {i} AND team_id = {self.team_id}")[0][0]
            max_segments.append(max_segment)
        return max_segments

    # for every consecutive emps needed it returns the number of segments the need lasted
    # e.g. 09:00 - 13:00 the team needed 3 emps so append 48
    def getDurationOfConsecutiveEmpsNeed(self, day):
        query = f"SELECT segment, emps_needed FROM teams_personnel_need_per_segment WHERE day={day} AND team_id = {self.team_id} ORDER BY segment"
        result = self.executeQuery(query)
        consecutive_nums = []
        count = 1
        first_val = True
        for res in result:
            if(res[1] == 0 and count == 1): continue
            elif(res[1] == 0 and count > 1):
                consecutive_nums.append(count)
                count = 1
                first_val = True
            else: 
                if(count == 1 and first_val): 
                    consecutive_value = res[1]
                    first_val = False
                    continue
                if(res[1] == consecutive_value):
                    count+=1
                if(res[1] != consecutive_value or res[0] == len(result) - 1):
                    consecutive_nums.append(count)
                    count = 1
                    first_val = True

        return consecutive_nums
    
    # gcd function for array of integers
    def GCD(self, array):
        if len(array) == 0: return 1
        _gcd = array[0]
        for n in range(len(array)):
            _gcd = gcd(_gcd, array[n])
        return _gcd
    
    # it takes the consecutive emps needs for every day and 
    # calculates the gcd to find the smallest possible shift
    # duration for the cp sat solver to split the shifts evenly
    def calculateMinimumShiftDuration(self, days):
        array = []
        # adds the minimum daily time an employee works from db
        array.append(self.dailyHoursToSegments(self.getMinEmployeesDailyHour()))

        for day in days:
            minimum_shift_of_day = self.GCD(self.getDurationOfConsecutiveEmpsNeed(day))
            array.append(minimum_shift_of_day)
        minimum_shift = self.GCD(array)
        return minimum_shift
    
    def exportNumOfShiftsPerDayBasedOnMinimumShift(self, day, minimum_shift):
        need_durations = self.getDurationOfConsecutiveEmpsNeed(day)
        shifts = 0
        for need in need_durations:
            count = 0
            while(count < need):
                shifts += 1
                count += minimum_shift
        return shifts
    

    def createShiftsForDay(self, day):
        query = f"SELECT segment, emps_needed FROM teams_personnel_need_per_segment WHERE day={day} AND emps_needed > 0 ORDER BY segment"
        result = self.executeQuery(query)
        minimum_shift = self.calculateMinimumShiftDuration(ALL_DAYS)
        i = 0
        count = 0
        while (i < len(result)):
            shift = Shift(day, count, result[i][0], result[i+minimum_shift-1][0], result[i][1])
            self.init_shifts.append(shift)
            i+=minimum_shift
            count+=1

    def initialize_shifts(self):
        team_employees = self.getEmployeesOfTeam()
        employees_ids = []
        for emp in team_employees:
            employees_ids.append(emp[0])
        init_shifts = {}
        for n in employees_ids:
            for s in self.init_shifts:
                init_shifts[(n, s.day, s.num)] = self.model.new_bool_var(f"shift_n{n}_d{s.day}_s{s.num}")
        return init_shifts
    

    # GET DATA FROM SHIFTS
    def getShiftsDictKeys(self):
        shifts_keys = []
        for key in self.shifts.keys():
            shifts_keys.append(key)
        return shifts_keys
    
    def getShiftsDictVals(self):
        shifts_vals = []
        for val in self.shifts.values():
            shifts_vals.append(val)
        return shifts_vals
    
    def getAllShiftDays(self):
        days = []
        for shift in self.getShiftsDictKeys():
            if (shift[1] not in days):
                days.append(shift[1])
        return days
    
    def getShiftsOfDay(self, day):
        shifts = set()
        for shift in self.getShiftsDictKeys():
            if (shift[1] == day):
                shifts.add(shift[2])
        return sorted(shifts)

    def getEmpsIds(self):
        ids = []
        for shift in self.getShiftsDictKeys():
            if (shift[0] not in ids):
                ids.append(shift[0])

    def shiftNumToStartTime(self, day, shift_num) -> int:
        for shift in self.init_shifts:
            if shift.day == day and shift.num == shift_num:
                return shift.s_time
    
    def shiftNumToEndTime(self, day, shift_num) -> int:
        for shift in self.init_shifts:
            if shift.day == day and shift.num == shift_num:
                return shift.e_time + 1
            
    def endTimeFromShiftDuration(self, shift_dur: str) -> str:
        return shift_dur.split(sep='-')[1]
    
    def startTimeFromShiftDuration(self, shift_dur: str) -> str:
        return shift_dur.split(sep='-')[0]

    # PRINTING



# functions for when the solver has found a solution
class SolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, init_shifts):
        super().__init__()
        self.shifts = shifts
        self.solution_count = 0
        self.seen = set()
        self.init_shifts = init_shifts

    def on_solution_callback(self):
        active = tuple(sorted(key for key, var in self.shifts.items() if self.Value(var))) #(n, d, s)
        if active in self.seen:
            return
        self.seen.add(active)

        self.solution_count += 1
        if (self.solution_count == 15):
            self.export_to_json(active)
        
        
    def export_to_json(self, solution):
        data = {"shifts": []}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, '..', '..', 'data', 'week_shifts.json')

        for n, d, s in solution:
            # find or create the employee
            emp = next((item for item in data["shifts"] if item["emp_id"] == n), None)
            if not emp:
                emp = {"emp_id": n, "employee_shifts": []}
                data["shifts"].append(emp)

            # find or create the day entry
            day_str = Scheduler.dayNumToString(self, d)
            day_entry = next((day for day in emp["employee_shifts"] if day_str in day), None)
            if not day_entry:
                day_entry = {day_str: []}
                emp["employee_shifts"].append(day_entry)

            # build shift string
            start = Scheduler.segmentToStringFormat(self, Scheduler.shiftNumToStartTime(self, d, s))
            end = Scheduler.segmentToStringFormat(self, Scheduler.shiftNumToEndTime(self, d, s))
            shift_str = f"{start}-{end}"

            # append the shift to that day
            # if there are 2 consecutive shifts append them as one continuous
            if (len(day_entry[day_str]) > 0):
                if (Scheduler.endTimeFromShiftDuration(self, day_entry[day_str][len(day_entry[day_str])-1]) == start):
                    day_entry[day_str][len(day_entry[day_str])-1] = Scheduler.startTimeFromShiftDuration(self, day_entry[day_str][len(day_entry[day_str])-1]) + '-' + end
                else:
                    day_entry[day_str].append(shift_str)
            else:
                day_entry[day_str].append(shift_str)
            
            
        with open(json_path, 'w+', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()