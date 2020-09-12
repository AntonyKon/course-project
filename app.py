from flask import Flask, request, render_template, redirect, url_for
from dbconnect import dbconnect

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def proccheck(conn, l_year, l_month):
    mycursor = conn.cursor()

    sqlreq = 'SELECT COUNT(*) FROM calendar ' \
             'WHERE ot_year=%s AND ot_month=%s'
    mycursor.execute(sqlreq, (l_year, l_month))
    result = mycursor.fetchall()

    return result[0][0]


@app.route('/request1', methods=['GET', 'POST'])
def request1():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `equipment`.`eq_id`, `equipment`.`eq_name`, `employee`.`surname`, `protocol`.`status`, ' \
             '`protocol`.`test_date`' \
             'FROM `equipment`' \
             'JOIN `protocol`' \
             'ON `equipment`.`eq_id`=`protocol`.`equip`' \
             'JOIN `employee`' \
             'ON `protocol`.`staff`=`employee`.`emp_id`' \
             'WHERE YEAR(`protocol`.`test_date`)=2017 AND MONTH(`protocol`.`test_date`)=3'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['id', 'name', 'employee', 'status', 'date']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=1, table=result)


@app.route('/request2', methods=['GET', 'POST'])
def request2():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `employee`.`surname`, COUNT(`protocol`.`staff`)' \
             'FROM `employee`' \
             'JOIN `protocol`' \
             'ON `employee`.`emp_id`=`protocol`.`staff`' \
             'WHERE YEAR(`protocol`.`test_date`)=2017 AND MONTH(`protocol`.`test_date`)=3 ' \
             'GROUP BY `employee`.`surname`'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['employee', 'count']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=2, table=result)


@app.route('/request3', methods=['GET', 'POST'])
def request3():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `equipment`.* ' \
             'FROM `equipment` ' \
             'JOIN `protocol` ON `equipment`.`eq_id`=`protocol`.`equip` ' \
             'WHERE `protocol`.`test_date`=(' \
             'SELECT MIN(`test_date`) FROM `protocol`' \
             ') ' \
             'GROUP BY `protocol`.`test_date`'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['id', 'name', 'producer', 'type']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=3, table=result)


@app.route('/request4', methods=['GET', 'POST'])
def request4():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `employee`.`surname`' \
             'FROM `employee` ' \
             'LEFT JOIN `protocol` ' \
             'ON `employee`.`emp_id`=`protocol`.`staff` ' \
             'LEFT JOIN `equipment` ' \
             'ON `protocol`.`equip`=`equipment`.`eq_id` ' \
             'WHERE `equipment`.`eq_name`="XXX" ' \
             'GROUP BY `surname`'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['employee']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=4, table=result)


@app.route('/request5', methods=['GET', 'POST'])
def request5():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `surname`' \
             'FROM `employee` ' \
             'LEFT JOIN `protocol` ON `employee`.`emp_id`=`protocol`.`staff` ' \
             'WHERE `protocol`.`test_id` IS NULL'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['employee']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=5, table=result)


@app.route('/request6', methods=['GET', 'POST'])
def request6():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    sqlreq = 'SELECT `employee`.`surname` ' \
             'FROM `employee` ' \
             'WHERE `employee`.`emp_id` NOT IN (' \
             'SELECT `protocol`.`staff` ' \
             'FROM `protocol` ' \
             'WHERE YEAR(`protocol`.`test_date`)=2017 AND MONTH(`protocol`.`test_date`)=3 ' \
             'GROUP BY `protocol`.`staff`' \
             ')'

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['employee']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('results.html', ans=6, table=result)


@app.route('/proc', methods=['GET', 'POST'])
def proc():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    if request.form.get('send') is None:
        return render_template('proc.html')

    l_year = request.form['year']
    l_month = request.form['month']

    strnum = proccheck(conn, l_year, l_month)
    if strnum:
        return render_template('proc.html', proc=1)

    mycursor = conn.cursor()
    mycursor.callproc('getdepartment', (l_year, l_month))
    conn.commit()

    return render_template('proc.html', proc=0)


@app.route('/report', methods=['GET', 'POST'])
def report():
    conn = dbconnect('equipment_testing')
    if conn is None:
        return render_template('results.html', ans=0)

    if request.form.get('send') is None:
        return render_template('otchet.html')

    year = request.form['year']
    month = request.form['month']

    condition = 'WHERE '

    if year:
        year = 'ot_year=' + year
    if month:
        month = 'ot_month=' + month

    if year != '' and month != '':
        condition += year + ' AND ' + month
    elif year == '' and month == '':
        condition += '1'
    else:
        condition += year + month

    sqlreq = 'SELECT * FROM `calendar` ' + condition

    mycursor = conn.cursor()
    mycursor.execute(sqlreq)
    result = mycursor.fetchall()

    reskeys = ['id', 'year', 'month', 'department', 'tests']

    result = list(map(lambda x: dict(zip(reskeys, x)), result))
    return render_template('otchet.html', otchet=1, table=result)


@app.route('/')
def menu():
    if request.args.get('r') is None:
        return render_template('menu.html')
    num = request.args['r']
    if num == '1':
        return redirect(url_for('request1'))
    elif num == '2':
        return redirect(url_for('request2'))
    elif num == '3':
        return redirect(url_for('request3'))
    elif num == '4':
        return redirect(url_for('request4'))
    elif num == '5':
        return redirect(url_for('request5'))
    elif num == '6':
        return redirect(url_for('request6'))
    elif num == 'proc':
        return redirect(url_for('proc'))
    else:
        return redirect(url_for('report'))


if __name__ == '__main__':
    app.run(debug=True)
