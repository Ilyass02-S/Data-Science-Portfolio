class PayrollSysytem:
    def calculate_payroll(self,employees):
        for employee in employees:
            print("Employee Payroll")
            print("================")
            print("Payroll for:",employee.id,"-",employee.name)
            print("- Check amount:",employee.calculate_salary())
            print("")
class Employee:
    def __init__(self,id,name):
        self.id=id
        self.name=name
    def ask_name(self):
        try:
            self.name=input("Please enter employee name:")
        except:
            self.name=""
class SalaryEmployee(Employee):
    def __init__(self, id,name,monthly_salary):
        super().__init__(id, name)
        self.monthly_salary=int(monthly_salary)
    def ask_salary(self):
            self.monthly_salary=int(input("Please enter monthly salary:"))
    def calculate_salary(self):
        return self.monthly_salary
class HourlyEmployee(Employee):
	def __init__(self,id,name,hour_rate,hours_worked):
		super().__init__(id,name)
		self.hour_rate=hour_rate
		self.hours_worked= hours_worked
	def ask_salary(self):
		self.hours_worked=int(input("Please enter hours worked:"))
		self.hour_rate=int(input("Please enter hour rate:"))
	def calculate_salary(self):
		return self.hour_rate * self.hours_worked
class CommissionEmployee(Employee):
	def __init__(self,id,name,monthly_salary,commission):
		super().__init__(id,name)
		self.commission=commission
		self.monthly_salary=monthly_salary
	def ask_salary(self):
		self.monthly_salary=int(input("Please enter monthly salary:"))
		self.commission=int(input("Please enter commission:"))
	def calculate_salary(self):
		return self.monthly_salary + self.commission
def SalaryMenu(employees):
    id = max(employee.id for employee in employees) + 1 if employees else 1
    while True:
            salarytype=int(input("""Please enter salary type:
(1) monthly
(2) hourly
(3) commission
(0) Quit
"""))
            if salarytype==1:
                employee=SalaryEmployee(id,"",0)
                SalaryEmployee.ask_name(employee)
                SalaryEmployee.ask_salary(employee)
                employees.append(employee)
                id += 1 
            elif salarytype == 2:
                employee=HourlyEmployee(id,"",0,0)
                HourlyEmployee.ask_name(employee)
                HourlyEmployee.ask_salary(employee)
                employees.append(employee)
                id += 1 
            elif salarytype == 3:
                employee=CommissionEmployee(id,"",0,0)
                CommissionEmployee.ask_name(employee)
                CommissionEmployee.ask_salary(employee)
                employees.append(employee)
                id += 1 
            elif salarytype == 0:
                break
            else:
                print("Incorrect selection.")  
    return employees

def ActionMenu():
    employees=[]
    while True:
        print("""(1) Add employee to employees
(2) Write employees to file
(3) Read employees from file
(4) Print payroll
(0) Quit
""")
        selection = int(input("Please select one: "))
        if selection == 1:
            employees = SalaryMenu(employees)
        elif selection == 2:
            myfile = open("employee.csv", "w")
            for employee in employees:
                if isinstance(employee, SalaryEmployee):
                    employee_data = f"{employee.id},{employee.name},M,{employee.calculate_salary()}\n"
                elif isinstance(employee, HourlyEmployee):
                    employee_data = f"{employee.id},{employee.name},H,{employee.hours_worked},{employee.hour_rate}\n"
                elif isinstance(employee, CommissionEmployee):
                    employee_data = f"{employee.id},{employee.name},C,{employee.monthly_salary},{employee.commission}\n"
                myfile.write(employee_data)
            myfile.close()
            print(len(employees), " employee(s) added to employee.csv")
        elif selection == 3:
            myfile = open("employee.csv", "r") 
            content = myfile.readlines()
            employees.clear()
            for line_number, line in enumerate(content, start=1):
                line = line.strip()
                elements = line.split(',')
                if len(elements) == 4:  # Check for the number of elements
                    id, name, salary_type, salary_value = elements
                    if salary_type == 'M':
                        employees.append(SalaryEmployee(int(id), name, int(salary_value)))
                else:
                    id,name,salary_type,v1,v2=elements
                    if salary_type == 'H':  
                        employees.append(HourlyEmployee(int(id), name, int(v1),int(v2)))
                    elif salary_type == 'C':
                        employees.append(CommissionEmployee(int(id), name, int(v1), int(v2)))
            myfile.close()
            print(len(employees), " employee(s) read from employee.csv")

        elif selection == 4:
            payroll_system = PayrollSysytem()  
            payroll_system.calculate_payroll(employees)  
        elif selection == 0:
            print("Service shutting down, thank you.")
            break
        else:
            print("Incorrect selection")

ActionMenu()