import os
import platform
import subprocess
import sys 
import yaml
import argparse
import markdown
import pdfkit
import plotly.graph_objects as go
from mako.template import Template

class MonthlyBudget():
    """Analyzing and visualizing montly budgets"""
    def __init__(self, name, yml_name, output, data):
        self.name = name
        if output:
            self.output = output if output[-1] == "/" else output + "/"
            self.dir = os.path.join(os.path.dirname(self.output), self.name.replace(" ", "_").lower() + "_budget")
        else:
            self.dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.name.replace(" ", "_").lower() + "_budget")
        try:
            os.makedirs(self.dir)
        except FileExistsError:
            print("INFO: Directory Exists.")
            pass
        self.data = self.prettyfy(data)['Montly Budget']
        self.data['analytics'] = {}
        self.data['analytics']['name'] = self.name
        self.data['analytics']['yml_name'] = yml_name
        self.node_step_x = 1/5
        self.node_labels = []
        self.node_x = []
        self.link_source = []
        self.link_target = []
        self.link_value = []
        self.link_color = []
        self.build_node_labels()
        self.analyze_income()
        self.analyze_expenses()
        self.analyze_taxes()
        self.analyze_retirement()
        self.analyze_savings()
        self.analyze_budget()

    def prettyfy(self, dict1):
        dict2 = {}
        for k in dict1.keys():
            if isinstance(dict1[k], dict):
                dict2[k.replace("_", " ").title()] = self.prettyfy(dict1[k])
            else:
                dict2[k.replace("_", " ").title()] = dict1[k]
        return dict2

    def recursive_items(self, dictionary):
        """Helper function to enumerate all keys in a nested dictionary"""
        for key, value in dictionary.items():
            if type(value) is dict:
                yield (key, value)
                yield from self.recursive_items(value)
            else:
                yield (key, value)

    def build_node_labels(self):
        """Enumerate all nodes in the Sankey diagram based on imported data"""
        for key,value in self.recursive_items(self.data):
            self.node_labels.append(key)
            if key in ('Jordan Salary', 'Taylor Salary', 'Wysocke Design',
                       'Bank Interest', 'Credit Card Rewards', 'Dividends'):
                self.node_x.append(0*self.node_step_x)
            elif key in ('Earned Income', 'Passive Income'):
                self.node_x.append(1*self.node_step_x)
            elif key in ('Income'):
                self.node_x.append(2*self.node_step_x)
            elif key in ( 'Taxes', 'Expenses', 'Retirement', 'Savings'):
                self.node_x.append(3*self.node_step_x)
            elif key in ('Personal Expenses', 'Home Expenses',
                         'Vehicle Expenses', 'Insurance Premiums',
                         'Subscriptions'):
                self.node_x.append(4*self.node_step_x)
            else:
                self.node_x.append(5*self.node_step_x)
        self.node_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.52,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0]

    def add_link_data(self, source, target, value, color):
        """Helper function to build the source, target, and value arrays"""
        if source not in self.node_labels:
            self.node_labels.append(source)
        if target not in self.node_labels:
            self.node_labels.append(target)
        self.link_source.append(self.node_labels.index(source))
        self.link_target.append(self.node_labels.index(target))
        self.link_value.append(value)
        self.link_color.append(color)

    def build_viz(self, output):
        """Generate the Sankey diagram"""
        node = dict(
              pad = 10,
              thickness = 10,
              line = dict(color = "black", width = 0.15),
              label = self.node_labels,
              color = "rgba(28,67,68,1)",
#              x = self.node_x,
#              y = self.node_y
              )
        link = dict(source = self.link_source,
                    target = self.link_target,
                    value = self.link_value,
                    color = self.link_color)
        data = go.Sankey(link = link,
                         node = node,
                         arrangement = 'freeform',
                         valueformat = '$,')
        fig = go.Figure(data)
        fig_title = self.name.capitalize() + " Monthly Budget"
        fig.update_layout(title_text=fig_title,
                          font=dict(size=10, color='white'),
                          hovermode='x', plot_bgcolor='black',
                          paper_bgcolor='black')
        fig.show()
        file_base_name = self.name.replace(" ", "_").lower()
        viz_file_name = self.dir + "/" + file_base_name
        fig.write_image(format="pdf", file=viz_file_name + "_budget_viz.pdf", width=1450, height=850)
        fig.write_html(viz_file_name + "_budget_viz.html")

    def analyze_budget(self):
        """Calculate budget-level metrics"""

        # Calculuate monthly net income
        self.data["analytics"]["net_income"] = round(self.data["analytics"]["income"] - self.data["analytics"]["expenses"] - self.data["analytics"]["taxes"] - \
                          self.data["analytics"]["retirement"] - self.data["analytics"]["savings"], 2)
        self.add_link_data("Income", "Net Income", self.data["analytics"]["net_income"], "rgba(0,255,0,0.3)")
        self.node_x.append(3*self.node_step_x)
        self.node_y.append(0.99)

        # Calculuate discretionary income
        dis_inc = self.data["analytics"]["income"] - self.data["analytics"]["taxes"] - self.data["analytics"]["expenses"] - self.data["analytics"]["retirement"]
        if dis_inc > 0:
            self.data["analytics"]["discretionary_income"] = dis_inc
        else:
            self.data["analytics"]["discretionary_income"] = 0
        # Calculuate potential annual metrics
        self.data["analytics"]["annual_income"] = self.data["analytics"]["income"] * 12
        self.data["analytics"]["annual_expenses"] = self.data["analytics"]["expenses"] * 12
        self.data["analytics"]["annual_taxes"] = self.data["analytics"]["taxes"] * 12
        self.data["analytics"]["annual_retirement"] = self.data["analytics"]["retirement"] * 12
        self.data["analytics"]["annual_savings"] = self.data["analytics"]["savings"] * 12
        self.data["analytics"]["annual_net_income"] = self.data["analytics"]["net_income"] * 12

        self.data["analytics"]["annual_expenses_prct"] = self.data["analytics"]["annual_expenses"]/self.data["analytics"]["annual_income"]
        self.data["analytics"]["annual_taxes_prct"] = self.data["analytics"]["annual_taxes"]/self.data["analytics"]["annual_income"]
        self.data["analytics"]["annual_retirement_prct"] = self.data["analytics"]["annual_retirement"]/self.data["analytics"]["annual_income"]
        self.data["analytics"]["annual_savings_prct"] = self.data["analytics"]["annual_savings"]/self.data["analytics"]["annual_income"]
        self.data["analytics"]["annual_net_income_prct"] = self.data["analytics"]["annual_net_income"]/self.data["analytics"]["annual_income"]

        # Calculate mortgage-to-income ratio
        self.data["analytics"]["total_mortgage"] = self.data["Expenses"]["Home Expenses"]["Mortgage"] +\
                                               self.data["Expenses"]["Home Expenses"]["Real Estate Tax"] +\
                                               self.data["Expenses"]["Home Expenses"]["Homeowners Insurance"]
        self.data["analytics"]["mortgage_income_ratio"] = (self.data["analytics"]["total_mortgage"] /\
                                                          self.data["analytics"]["income"]) * 100

        # Calculuate debt-to-income ratio
        self.data["analytics"]["total_debt"] = self.data["analytics"]["total_mortgage"] +\
                                               self.data["Expenses"]["Vehicle Expenses"]["Car Loan"]

        self.data["analytics"]["debt_income_ratio"] = (self.data["analytics"]["total_debt"] /\
                                                      self.data["analytics"]["income"]) * 100
                                                      

        # Calculuate suggested emergency fund
        self.data["analytics"]["emergency_fund"] = self.data["analytics"]["expenses"] * 6

        # Calculuate savings rate
        self.data["analytics"]["savings_rate"] = (self.data["analytics"]["savings"] + self.data["analytics"]["retirement"]) / self.data["analytics"]["income"]

        # Calculuate FI number
        self.data["analytics"]["fi_number"] = self.data["analytics"]["expenses"] * 12 * 25

    def analyze_income(self):
        """Add income source, target, and value arrays"""
        self.data["analytics"]["earned_income"] = 0.00
        self.data["analytics"]["passive_income"] = 0.00
        for budget_cat,budget_values in self.data.items():
            if budget_cat == "Income":
                for income_cat,income_values in budget_values.items():
                    if income_cat == "Earned Income":
                        for income_subcat,subcat_value in income_values.items():
                            self.data["analytics"]["earned_income"] += subcat_value
                            self.add_link_data(income_subcat, income_cat, subcat_value, "rgba(0,255,0,0.3)")
                        self.add_link_data(income_cat, budget_cat, self.data["analytics"]["earned_income"], "rgba(0,255,0,0.3)")
                    elif income_cat == "Passive Income":
                        for income_subcat,subcat_value in income_values.items():
                            self.data["analytics"]["passive_income"] += subcat_value
                            self.add_link_data(income_subcat, income_cat, subcat_value, "rgba(0,255,0,0.3)")
                        self.add_link_data(income_cat, budget_cat, self.data["analytics"]["passive_income"], "rgba(0,255,0,0.3)")
        self.data["analytics"]["income"] = round(self.data["analytics"]["earned_income"] + self.data["analytics"]["passive_income"], 2)

    def analyze_taxes(self):
        """Add tax source, target, and value arrays"""
        # Calculate taxable income
        standard_deduction = 12550/12
        self.data["analytics"]["taxable_income"] = round(self.data["analytics"]["income"] - (standard_deduction * 2), 2)
        # Compute federal income taxes based on  MFJ
        if self.data["analytics"]["taxable_income"] <= 20550/12:
            self.data["analytics"]["high_tax_rate"] = 0.1
            self.fed_income_taxes = self.data["analytics"]["taxable_income"] * 0.1
        elif self.data["analytics"]["taxable_income"] <= 83550/12: 
            self.data["analytics"]["high_tax_rate"] = 0.12
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 20550/12) * 0.12 + 2055/12
        elif self.data["analytics"]["taxable_income"] <= 178150/12:
            self.data["analytics"]["high_tax_rate"] = 0.22
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 83550/12) * 0.22 + 9615/12
        elif self.data["analytics"]["taxable_income"] <= 340100/12:
            self.data["analytics"]["high_tax_rate"] = 0.24
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 178150/12) * 0.24 + 30427/12
        elif self.data["analytics"]["taxable_income"] <= 431900/12:
            self.data["analytics"]["high_tax_rate"] = 0.32
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 340100/12) * 0.32 + 69295/12
        elif self.data["analytics"]["taxable_income"] <= 647850/12:
            self.data["analytics"]["high_tax_rate"] = 0.35
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 431900/12) * 0.35 + 98671/12
        else:
            self.data["analytics"]["high_tax_rate"] = 0.37
            self.fed_income_taxes = (self.data["analytics"]["taxable_income"] - 647850/12) * 0.37 + 174253.5/12
        # Dedeuct montly child tax credit
        child_tax_credit = 2000/12
        self.fed_income_taxes = self.fed_income_taxes - child_tax_credit
        self.data["analytics"]["fed_income_taxes"] = round(self.fed_income_taxes, 2)
        self.add_link_data("Taxes", "Federal Income", self.data["analytics"]["fed_income_taxes"], "rgba(255,0,0,0.3)")

        # Compute Colorado state income tax, 4.55% in 2022
        self.data["analytics"]["state_income_taxes"] = round(0.0455 * self.data["analytics"]["income"], 2)
        self.add_link_data("Taxes", "State Income", self.data["analytics"]["state_income_taxes"], "rgba(255,0,0,0.3)")
        
        # Compute FICA taxes
        oasdi_tax_tot = 0
        med_tax_tot = 0
        for income,value in self.data["Income"]["Earned Income"].items():
            income_name = income.replace(" ","_").lower() 
            oasdi_name = income_name + "_oasdi_tax"
            med_name = income_name + "_med_tax"
            # Compute OASDI taxes (use gross income, not taxable income)
            if value < 147000/12:
                oasdi_tax = round(value * 0.062, 2)
            else:
                oasdi_tax = round((147000/12) * 0.062, 2)
               
            # Compute Medicare taxes (use gross income, not taxable income)
            if self.data["analytics"]["income"] <= 250000/12: 
                med_tax = round(value * 0.0145, 2)
            else: #additional medicare tax of 0.9%
                extra_ratio = (self.data["analytics"]["income"] - (250000/12)) / self.data["analytics"]["income"]
                med_tax = round(value * 0.0145 + (value * extra_ratio) * 0.009, 2)

            if "Salary" not in income and "Bonus" not in income: #assume tax is for business income, so you pay double
                oasdi_tax = oasdi_tax * 2
                med_tax = med_tax * 2

            oasdi_tax_tot += oasdi_tax
            med_tax_tot += med_tax

            self.data["analytics"][oasdi_name] = round(oasdi_tax, 2)
            self.data["analytics"][med_name] = round(med_tax, 2)
 
            self.add_link_data("Taxes", oasdi_name.replace("_", " ").title(), oasdi_tax, "rgba(255,0,0,0.3)")
            self.add_link_data("Taxes", med_name.replace("_", " ").title(), med_tax, "rgba(255,0,0,0.3)")

        self.data["analytics"]["oasdi_tax"] = round(oasdi_tax_tot, 2)
        self.data["analytics"]["med_tax"] = round(med_tax_tot, 2)
        self.data["analytics"]["fica_taxes"] = round(self.data["analytics"]["oasdi_tax"] + self.data["analytics"]["med_tax"], 2)

        self.data["analytics"]["taxes"] = self.data["analytics"]["fed_income_taxes"] + self.data["analytics"]["state_income_taxes"] + self.data["analytics"]["oasdi_tax"] + self.data["analytics"]["med_tax"]
        self.add_link_data("Income", "Taxes", self.data["analytics"]["taxes"], "rgba(255,0,0,0.3)")

        # Calculate effective tax rates
        self.data["analytics"]["effective_fed_tax_rate"] = round(self.data["analytics"]["fed_income_taxes"] / self.data["analytics"]["income"], 6)
        self.data["analytics"]["effective_state_tax_rate"] = round(self.data["analytics"]["state_income_taxes"] / self.data["analytics"]["income"], 6)
        self.data["analytics"]["effective_fica_tax_rate"] = round(self.data["analytics"]["fica_taxes"] / self.data["analytics"]["income"], 6)
        self.data["analytics"]["effective_tax_rate"] = round(self.data["analytics"]["taxes"] / self.data["analytics"]["income"], 6)

    def analyze_retirement(self):
        """Add retirement source, target, and value arrays"""
        self.data["analytics"]["retirement"] = 0.00
        for budget_cat,budget_value in self.data.items():
            if budget_cat == "Retirement":
                for retire,retire_value in budget_value.items():
                    self.data["analytics"]["retirement"] += retire_value
                    self.add_link_data(budget_cat, retire, retire_value, "rgba(28,67,68,0.3)")
        self.data["analytics"]["retirement"] = round(self.data["analytics"]["retirement"], 2)
        self.add_link_data("Income", "Retirement", self.data["analytics"]["retirement"], "rgba(28,67,68,0.3)")
        # Retirement savings rate
        self.data["analytics"]["retire_savings_rate"] = (self.data["analytics"]["retirement"] + self.data["Savings"]["Supplemental Retirement"]) / self.data["analytics"]["income"]

    def analyze_savings(self):
        """Add savings source, target, and value arrays"""
        self.data["analytics"]["savings"] = 0.00
        for budget_cat,budget_value in self.data.items():
            if budget_cat == "Savings":
                for save,save_value in budget_value.items():
                    self.data["analytics"]["savings"] += save_value
                    self.add_link_data(budget_cat, save, save_value, "rgba(28,67,68,0.3)")
        self.data["analytics"]["savings"] = round(self.data["analytics"]["savings"], 2)
        self.add_link_data("Income", "Savings", self.data["analytics"]["savings"], "rgba(28,67,68,0.3)")

        # Flatten nested dictionaries, then sort highest to lowest
        flattened_savings = {}
        for key,value in self.recursive_items(self.data["Savings"]):
            if type(value) is not dict:
                flattened_savings[key] = value
        top_savings = dict(sorted(flattened_savings.items(), key=lambda item: item[1], reverse=True))
        self.data["analytics"]["top_savings"] = top_savings

    def analyze_expenses(self):
        """Add expense source, target, and value arrays"""
        self.data["analytics"]["personal_expenses"] = 0.00
        self.data["analytics"]["home_expenses"] = 0.00
        self.data["analytics"]["vehicle_expenses"] = 0.00
        self.data["analytics"]["insurance_premiums"] = 0.00
        self.data["analytics"]["subscriptions"] = 0.00
        for budget_cat,budget_values in self.data.items():
            if budget_cat == "Expenses":
                for expense_cat,expense_values in budget_values.items():
                    if expense_cat == "Personal Expenses":
                        for expense_subcat,subcat_value in expense_values.items():
                            self.data["analytics"]["personal_expenses"] += subcat_value
                            self.add_link_data(expense_cat, expense_subcat, subcat_value, "rgba(255,0,0,0.3)")
                        self.data["analytics"]["personal_expenses"] = round(self.data["analytics"]["personal_expenses"], 2)
                        self.add_link_data(budget_cat, expense_cat, self.data["analytics"]["personal_expenses"], "rgba(255,0,0,0.3)")
                    elif expense_cat == "Home Expenses":
                        for expense_subcat,subcat_value in expense_values.items():
                            self.data["analytics"]["home_expenses"] += subcat_value
                            self.add_link_data(expense_cat, expense_subcat, subcat_value, "rgba(255,0,0,0.3)")
                        self.data["analytics"]["home_expenses"] = round(self.data["analytics"]["home_expenses"], 2)
                        self.add_link_data(budget_cat, expense_cat, self.data["analytics"]["home_expenses"], "rgba(255,0,0,0.3)")
                    elif expense_cat == "Vehicle Expenses":
                        for expense_subcat,subcat_value in expense_values.items():
                            self.data["analytics"]["vehicle_expenses"] += subcat_value
                            self.add_link_data(expense_cat, expense_subcat, subcat_value, "rgba(255,0,0,0.3)")
                        self.data["analytics"]["vehicle_expenses"] = round(self.data["analytics"]["vehicle_expenses"], 2)
                        self.add_link_data(budget_cat, expense_cat, self.data["analytics"]["vehicle_expenses"], "rgba(255,0,0,0.3)")
                    elif expense_cat == "Insurance Premiums":
                        for expense_subcat,subcat_value in expense_values.items():
                            self.data["analytics"]["insurance_premiums"] += subcat_value
                            self.add_link_data(expense_cat, expense_subcat, subcat_value, "rgba(255,0,0,0.3)")
                        self.data["analytics"]["insurance_premiums"] = round(self.data["analytics"]["insurance_premiums"], 2)
                        self.add_link_data(budget_cat, expense_cat, self.data["analytics"]["insurance_premiums"], "rgba(255,0,0,0.3)")
                    elif expense_cat == "Subscriptions":
                        for expense_subcat,subcat_value in expense_values.items():
                            self.data["analytics"]["subscriptions"] += subcat_value
                            self.add_link_data(expense_cat, expense_subcat, subcat_value, "rgba(255,0,0,0.3)")
                        self.data["analytics"]["subscriptions"] = round(self.data["analytics"]["subscriptions"], 2)
                        self.add_link_data(budget_cat, expense_cat, self.data["analytics"]["subscriptions"], "rgba(255,0,0,0.3)")
        self.data["analytics"]["expenses"] = round(self.data["analytics"]["personal_expenses"] + self.data["analytics"]["home_expenses"] + \
                        self.data["analytics"]["vehicle_expenses"] + self.data["analytics"]["insurance_premiums"] + 
                        self.data["analytics"]["subscriptions"], 2)
        self.add_link_data("Income", "Expenses", self.data["analytics"]["expenses"], "rgba(255,0,0,0.3)")

        # Flatten nested dictionaries, then sort highest to lowest
        flattened_expenses = {}
        for key,value in self.recursive_items(self.data["Expenses"]):
            if type(value) is not dict:
                flattened_expenses[key] = value
        top_expenses = dict(sorted(flattened_expenses.items(), key=lambda item: item[1], reverse=True)[:5])
        self.data["analytics"]["top_expenses"] = top_expenses

    def create_report(self, output):
        report = Template(filename='templates/budget_analysis.md')
        kwargs = self.data["analytics"]
        report_md = report.render(**kwargs)
        file_base_name = self.name.replace(" ", "_").lower()
        report_file = self.dir + "/" + file_base_name + "_budget_report.md"
        with open(report_file, "w+") as file:
            file.write(os.path.join(self.dir, report_md))
        if platform.system() == 'Darwin':
            subprocess.call(('open', report_file))
        elif platform.system() == 'Windows':
            os.startfile(report_file)
        else:
            subprocess.call(('xdg-open', report_file))

#        html = markdown.markdown(report_md, extensions=['markdown.extensions.tables'])
#        pdfkit.from_string(html, 'report.pdf')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True,
                        help="Input YAML file containing monthly budget data.")
    parser.add_argument('-o', '--output', nargs='?', const=1, type=str, default="",
                        help="Output location for budget report markdown file.")
    parser.add_argument('-n', '--name', nargs='?', const=1, type=str, default="Untitled Budget",
                        help="Name of the budget.")
    args = parser.parse_args()

    yml = open(args.input, 'r')
    data = yaml.full_load(yml)
    budget = MonthlyBudget(args.name, args.input, args.output, data)
    budget.build_viz(args.output)
    budget.create_report(args.output)
