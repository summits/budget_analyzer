<h1 style="text-align:center"> ${name} Monthly Budget Report </h1>
<%! from time import strftime as time %>
<p style="text-align:center;font-style:italic">Prepared on ${"%m/%d/%Y at %H:%M:%S" | time} based on input data from "${yml_name}"</p>

<h2> Monthly Budget Summary </h2>

<center>

| ITEM | AMOUNT |
| ---- | -----: |
| <span style="color:green">Total Gross Income</span> | <span style="color:green">${'${:,.2f}'.format(income)}</span> | 
| Total Taxes | ${'${:,.2f}'.format(taxes)} |
| <span style="color:red">Total Expenses</span> | <span style="color:red">${'${:,.2f}'.format(expenses)}</span> |
| Retirement Savings | ${'${:,.2f}'.format(retirement)} |
| Regular Savings | ${'${:,.2f}'.format(savings)} |
% if str(net_income)[0] == "-":
| <span style="color:red">**NET INCOME**</span> | <span style="color:red">**${'${:,.2f}'.format(net_income)}**</span> |
% else:
| <span style="color:green">**NET INCOME**</span> | <span style="color:green">**${'${:,.2f}'.format(net_income)}**</span> |
% endif

![Budget Sankey Diagram](${name.replace(" ", "_").lower()}_budget_viz.pdf)

_[Interactive Sankey Diagram](${name.replace(" ", "_").lower()}_budget_viz.html)_

</center>

<h3> Monthly Metrics Snapshot </h3>

<center>

| METRIC | VALUE |
| ------ | ----: |
| Total Debts | ${'${:,.2f}'.format(total_debt)} |
| Debt-to-Income Ratio | ${'{:,.2f}%'.format(debt_income_ratio)} |
| Mortgage-to-Income Ratio | ${'{:,.2f}%'.format(mortgage_income_ratio)} |
| Financial Independence Number | ${'${:,.0f}'.format(fi_number)} |
| Highest marginal federal income tax rate | ${"{:.0%}".format(high_tax_rate)} |
| Suggested Emergency Fund |  ${'${:,.2f}'.format(emergency_fund)} |

</center>

<h2> Monthly Income Sources</h2>

<center>

| INCOME | AMOUNT |
| ------ | -----: |
| Earned Income | ${'${:,.2f}'.format(earned_income)} |
| Passive Income | ${'${:,.2f}'.format(passive_income)} |

</center>

<h2> Monthly Expenses </h2>

<h3> Expenses by Category </h3>

<center>

| CATEGORY | AMOUNT |
| -------- | -----: |
| Personal Expenses | ${'${:,.2f}'.format(personal_expenses)} |
| Home Expenses | ${'${:,.2f}'.format(home_expenses)} |
| Vehicle Expenses | ${'${:,.2f}'.format(vehicle_expenses)} |
| Insurance Premiums | ${'${:,.2f}'.format(insurance_premiums)} |
| Subscriptions | ${'${:,.2f}'.format(subscriptions)} |
| **TOTAL EXPENSES** | **${'${:,.2f}'.format(expenses)}** |

_*Suggested Emergency Fund: **${'${:,.2f}'.format(emergency_fund)}**_

</center>

<h3> Top 5 Expenses </h3>

<center>

| RANK | EXPENSE | AMOUNT |
| :---: | ------- | -----: |\
<% i=1 %>
% for key,value in top_expenses.items():
| ${i} | ${key} | ${'${:,.2f}'.format(value)} |\
<% i+=1 %>
% endfor

</center>

<h2> Monthly Tax Burden </h2>

Federal tax amounts are based on a total household monthly taxable income of **${'${:,.2f}'.format(taxable_income)}**

<center>

| TAX | AMOUNT | EFFECTIVE TAX RATE |
| --- | ------ | -----------------: |
| Total Federal Income | ${'${:,.2f}'.format(fed_income_taxes)} | ${"{:.2%}".format(effective_fed_tax_rate)}\* |
| Total State Income | ${'${:,.2f}'.format(state_income_taxes)} | ${"{:.2%}".format(effective_state_tax_rate)} |
| Total FICA | ${'${:,.2f}'.format(fica_taxes)} | ${"{:.2%}".format(effective_fica_tax_rate)} |
| **TOTAL TAXES** | **${'${:,.2f}'.format(taxes)}** | **${"{:.2%}".format(effective_tax_rate)}** |

\*_Highest marginal federal income tax rate is **${"{:.0%}".format(high_tax_rate)}**_

</center>

<h2> Monthly Savings </h2>

<h3> Sorted Savings </h3>

<center>

| ACCOUNT | AMOUNT |
| ------- | -----: |
% for key,value in top_savings.items():
| ${key} | ${'${:,.2f}'.format(value)} |
% endfor
| **TOTAL SAVINGS** | **${'${:,.2f}'.format(savings)}** |

</center>

<h3> Savings Metrics </h3>

<center>

| METRIC | VALUE |
| ------ | ----: |
| Savings Rate | ${"{:.2%}".format(savings_rate)} |
| Retirement Savings Rate\* | ${"{:.2%}".format(retire_savings_rate)} |
\*_Retirement savings rate includs supplemental retirement savings_

</center>

<h2> Annual Budget Metrics </h2>

<center>

| ITEM | TOTAL | % OF GROSS INCOME |
| --- | ------ | :---------------: |
| <span style="color:green">Annual Income</span> | <span style="color:green">${'${:,.2f}'.format(annual_income)}</span> | 100% |
| <span style="color:red">Annual Tax Burden</span> | <span style="color:red">${'${:,.2f}'.format(annual_taxes)}</span> | ${"{:.2%}".format(annual_taxes_prct)} |
| <span style="color:red">Annual Expenses</span> | <span style="color:red">${'${:,.2f}'.format(annual_expenses)}</span> | ${"{:.2%}".format(annual_expenses_prct)} |
| Annual Retirement Savings | ${'${:,.2f}'.format(annual_retirement)} | ${"{:.2%}".format(annual_retirement_prct)} |
| Annual Other Savings | ${'${:,.2f}'.format(annual_savings)} | ${"{:.2%}".format(annual_savings_prct)} |
% if str(net_income)[0] == "-":
| <span style="color:red">**Annual Net Income**</span> | <span style="color:red">**${'${:,.2f}'.format(annual_net_income)}**</span> | ${"{:.2%}".format(annual_net_income_prct)} |
% else:
| <span style="color:green">**Annual Net Income**</span> | <span style="color:green">**${'${:,.2f}'.format(annual_net_income)}**</span> | ${"{:.2%}".format(annual_net_income_prct)} |
% endif

</center>
