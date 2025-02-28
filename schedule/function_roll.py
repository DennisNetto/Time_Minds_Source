import info.models
from info.models import *
from users.models import Profile
from datetime import datetime, timedelta, date
from calendar import monthrange


# Done
# Sees if a recshift has any overtime.
def recovertime(staffid, list, start, end, alter):
    final = 0
    shiftsced = False
    overtimehours = 12
    rehours = 0
    re = ['', '']
    for i in list:
        # shiftsced = Shift.objects.filter(staff_id=staffid, shift_date=i)
        if shiftsced:
            for o in shiftsced:
                min_s = o.scheduled_start.minute / 60
                min_e = o.scheduled_end.minute / 60
                final = final + (o.scheduled_end.hour + min_e) - (o.scheduled_start.hour + min_s)

        newhours = (end.hour + end.minute) - (start.hour + start.minute)
        total = newhours + final
        if total > overtimehours:
            rehours += 1
    if 'make1' in alter:
        re[0] = False
        return re

    if rehours != 0:
        re[0] = True
        re[1] = rehours
        return re
    else:
        re[0] = False
        return re


# Done imp
# Finds shifts that intersect from recurring shifts.
def recintersection(list, client_id, staff_id, start, end, rec_id):
    sna = 0
    cna = 0
    insectshiftclient = ''
    insectshiftstaff = ''
    re = ['', '']
    for i in list:
        try:
            insectshiftclient = Shift.objects.get(scheduled_start__range=(str(start), str(end)),
                                                  scheduled_end__range=(str(start), str(end)), staff_id=staff_id,
                                                  shift_date=str(i))

            fiald_value = insectshiftclient.rec_id
            if int(rec_id) == int(fiald_value):
                False
            else:
                cna += 1
        except info.models.Shift.DoesNotExist:
            if insectshiftclient:
                None
        except info.models.Shift.MultipleObjectsReturned:
            cna += 1
        try:
            insectshiftstaff = Shift.objects.get(scheduled_start__range=(str(start), str(end)),
                                                 scheduled_end__range=(str(start), str(end)), client_id=client_id,
                                                 shift_date=str(i))
            fiald_value = insectshiftclient.rec_id
            if int(rec_id) == int(fiald_value):
                False
            else:
                sna += 1
        except info.models.Shift.DoesNotExist:
            if insectshiftstaff:
                None
        except info.models.Shift.MultipleObjectsReturned:
            sna += 1
    if cna or sna != 0:
        if cna != 0:
            re[0] = True
            re[1] = 'Client has ' + str(cna) + ' days that conflict with this recurring shift'
        if sna != 0:
            re[0] = True
            re[1] = 'Staff has ' + str(sna) + ' days that conflict with this recurring shift'
        return re
    else:
        re[0] = False
        return re


# Done imp
# Sees if a client is over there mounthly hours but for a rec shift.
def rechours(list, client_id, start, end):
    count = -1
    final = 0
    alter = 0
    message = ''
    min_s = start.minute / 60
    min_e = end.minute / 60
    total = (end.hour + min_e) - (start.hour + min_s)
    mounths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    letterM = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i in list:
        date = i[6]
        date = int(date) - 1
        mounths[date] += 1
    max = Client.objects.filter(client_id=client_id).values_list('client_max_hours', flat=True)
    for i in mounths:
        count += 1
        alter = count + 1
        i = i - alter
        final = final + (i * total)
        if final > max[0]:
            message = message + (str(letterM[count]) + ' ')
            alter = 0
            final = 0
    return message


# Done revition 1
# This function sees if a shift intersects with another shift.
def intersect(date, start, end, cli_id, staff_id, shiftid):
    try:
        insectshiftclient = Shift.objects.get(scheduled_start__range=(str(start), str(end)),
                                              scheduled_end__range=(str(start), str(end)), client_id=cli_id,
                                              shift_date=str(date))
        fiald_value = insectshiftclient.shift_id
    except info.models.Shift.DoesNotExist:
        insectshiftclient = False
    try:
        insectshiftstaff = Shift.objects.get(scheduled_start__range=(str(start), str(end)),
                                             scheduled_end__range=(str(start), str(end)), staff_id=staff_id,
                                             shift_date=str(date))
        fiald_value = insectshiftstaff.shift_id
    except info.models.Shift.DoesNotExist:
        insectshiftstaff = False
    re = ['', '']
    if insectshiftclient or insectshiftstaff:
        if insectshiftstaff:
            if int(fiald_value) == int(shiftid):
                re[0] = False
                return re
            re[0] = True
            re[1] = 'Staff'
            return re
        else:
            if int(fiald_value) == int(shiftid):
                re[0] = False
                return re
            re[0] = True
            re[1] = 'Client'
            return re
    else:
        re[0] = False
        return re


# Done imp
# converts a number date to a sql query.
def getdayofweek(t):
    theday = {0: Profile.objects.exclude(mon_avail=' - '), 1: Profile.objects.exclude(tue_avail=' - '),
              2: Profile.objects.exclude(wed_avail=' - '), 3: Profile.objects.exclude(thu_avail=' - '),
              4: Profile.objects.exclude(fri_avail=' - '), 5: Profile.objects.exclude(sat_avail=' - '),
              6: Profile.objects.exclude(sun_avail=' - ')}
    return theday[t]


# Done imp
# This function sees if a client has hours left in the mounth
def clienthours(shiftdate, clientid, start, end):
    shiftdate = str(shiftdate).split("-")
    month = str(shiftdate[0]) + '-' + str(shiftdate[1])
    clientshifts = Shift.objects.filter(client_id=clientid, shift_date__contains=month)
    final = 0
    for i in clientshifts:
        min_s = i.scheduled_start.minute / 60
        min_e = i.scheduled_end.minute / 60
        total = i.scheduled_end.hour + min_e - i.scheduled_start.hour + min_s
        final = final + total
    max = Client.objects.filter(client_id=clientid).values_list('client_max_hours', flat=True)
    shifttime = end.hour + end.minute - start.hour + start.minute
    final = final + shifttime
    re = ['', max[0], final]
    if int(max[0]) <= final:
        re[0] = True
        return re
    else:
        re[0] = False
        return re


# Done
# sees if the worker goes over overtime (change overtimehours to alter overtime)
def shiftovertime(staffid, shiftdate, start, end, alter):
    shiftsced = Shift.objects.filter(staff_id=staffid, shift_date=shiftdate)
    final = 0
    overtimehours = 12
    if shiftsced:
        for i in shiftsced:
            min_s = i.scheduled_start.minute / 60
            min_e = i.scheduled_end.minute / 60
            final = final + (i.scheduled_end.hour + min_e) - (i.scheduled_start.hour + min_s)

    newhours = (end.hour + end.minute) - (start.hour + start.minute)
    total = newhours + final
    if 'make1' in alter:
        return False
    if total > overtimehours:
        return True
    else:
        return False


# Done imp
# Makes a list of shifts to be scheduled from start to end dates.
def recshiftdays(startdate, enddate):
    date1 = datetime.strptime(str(startdate), "%Y-%m-%d")
    d2 = datetime.strptime(str(enddate), "%Y-%m-%d")
    day1 = (date1 - timedelta(days=date1.weekday()))
    day2 = (d2 - timedelta(days=d2.weekday()))
    shiftnum = (day2 - day1).days / 7
    endday = date1
    count = 1
    shifts = ['Error'] * int(shiftnum + 1)
    shifts[0] = date1.strftime('%Y-%m-%d')
    while endday != d2:
        endday = date1 + timedelta(days=7)
        shifts[count] = endday.strftime('%Y-%m-%d')
        date1 = endday
        count += 1
    return shifts


# Done
def letterday(N):
    dayofweek = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri',
                 5: 'sat', 6: 'sun', }
    return dayofweek[N]


# Done imp
# gets a staff member by id and returns its value and name.
def getstaff(staffid):
    try:
        quryval = Profile.objects.filter(staff_id=staffid).values_list('staff_id', 'staff_fname', 'staff_lname')
        stval = 'value=' + str(quryval[0][0])
        stval1 = 'ID(' + str(quryval[0][0]) + ') ' + str(quryval[0][1]) + ', ' + str(quryval[0][2])
    except IndexError:
        stval = 'value='
        stval1 = 'Select a Staff Member:'

    re = [stval, stval1]
    return re


# Done imp
# Gets the department value
def getdepartment(clendepart):
    try:
        quryval = Department.objects.filter(dep_code=clendepart).values_list('dep_name', flat=True)
        progval = 'value=' + str(clendepart)
        progval1 = str(quryval[0])
    except IndexError:
        progval = 'value='
        progval1 = 'Select a Department:'

    re = [progval, progval1]
    return re


def getclient(cid):
    try:
        quryval = Client.objects.filter(client_id=cid).values_list('client_id', 'client_fname', 'client_lname')
        re = 'CID(' + str(quryval[0][0]) + ') ' + str(quryval[0][1]) + ', ' + str(quryval[0][2])
    except IndexError:
        re = 'Error'

    return re


# Done imp
# finds if the start and end of a recshift is the same day of the week.
def thorsday(start, end):
    start = str(start).split('-')
    end = str(end).split('-')
    day1 = datetime(int(start[0]), int(start[1]), int(start[2]))
    day2 = datetime(int(end[0]), int(end[1]), int(end[2]))
    day1 = day1.weekday()
    day2 = day2.weekday()
    if str(day1) == str(day2):
        return False
    else:
        return True


# Sees if the first day is sooner that the end.
def befores(start, end):
    start = str(start).split('-')
    end = str(end).split('-')
    day1 = datetime(int(start[0]), int(start[1]), int(start[2]))
    day2 = datetime(int(end[0]), int(end[1]), int(end[2]))
    if day1 > day2:
        return True
    else:
        return False


def shiftrender(switch, year, month, id):
    changer = ''
    date = str(year) + '-' + '0' + str(month)
    if switch == 's':
        changer = Shift.objects.filter(staff_id=id, shift_date__contains=date)
    elif switch == 'c':
        changer = Shift.objects.filter(client_id=id, shift_date__contains=date)
    elif switch == 'd':
        changer = Shift.objects.filter(dep_code=id, shift_date__contains=date)
    listarray = changer
    return listarray


def shiftrenderrec(switch, id):
    changer = ''
    if switch == 's':
        changer = RecShift.objects.filter(staff_id=id)
    elif switch == 'c':
        changer = RecShift.objects.filter(client_id=id)
    elif switch == 'd':
        changer = RecShift.objects.filter(dep_code=id)
    listarray = changer
    return listarray


def monthword(num):
    num = int(num)
    month = ''
    if num == 1:
        month = 'January'
    elif num == 2:
        month = 'February'
    elif num == 3:
        month = 'March'
    elif num == 4:
        month = 'April'
    elif num == 5:
        month = 'May'
    elif num == 6:
        month = 'June'
    elif num == 7:
        month = 'July'
    elif num == 8:
        month = 'Augest'
    elif num == 9:
        month = 'September'
    elif num == 10:
        month = 'October'
    elif num == 11:
        month = 'November'
    elif num == 12:
        month = 'December'
    return month


def approvesheet(people):
    stack = ''
    totalworked = 0
    totalclaimed = 0
    cells = ''
    start = """<table border='1'><tr><th>Staff Name:</th><th>Total Hours Scheduled/Claimed:</th><th>Review Timesheet</th></tr>"""
    end = '</table>'
    for i in people:
        totalclaimed = 0
        totalworked = 0
        shifts = Shift.objects.filter(status_code='Claimed', staff_id=i)
        worker = Profile.objects.filter(staff_id=i).values_list('staff_fname', 'staff_lname')
        for o in shifts:
            totalworked = totalworked + (int(o.scheduled_end.hour) + int((o.scheduled_end.minute / 60))) - (int(o.scheduled_start.hour) + int((o.scheduled_start.minute / 60)))
            totalclaimed = totalclaimed + (int(o.claimed_end.hour) + int((o.claimed_end.minute / 60))) - (int(o.claimed_start.hour) + int((o.claimed_start.minute / 60)))
        if totalworked == totalclaimed:
            tt = "<tr style='background-color: #AAFFAA'>"
        else:
            tt = "<tr style='background-color: #ed4747'>"
        cells = cells + tt + '<td>' + str(worker[0][0]) + ', ' + str(worker[0][1]) + '</td><td>' + str(
            totalworked) + '/' + str(totalclaimed) + '</td><td><a href="/approve/' + str(
            i) + '" class="btn btn-dark">Review</a></td></tr>'
    return start + cells + end


def convertTime(s):
    return datetime.strptime(s, '%H%M').strftime('%I:%M%p').lower()


def submithours(shifts, name, id):
    cell = ''
    end = '</table>'
    start = "<table border='1'><tr><th>Individual Served</th><th>Shift Date</th><th>Scheduled Hours</th><th>Claimed Hours</th><th>Approved start</th><th>Approved End</th><th>Save</th></tr>"
    for i in shifts:
        sstart = str(i.scheduled_start.hour) + str(i.scheduled_start.minute)
        send = str(i.scheduled_end.hour) + str(i.scheduled_end.minute)
        cstart = str(i.claimed_start.hour) + str(i.claimed_start.minute)
        cend = str(i.claimed_end.hour) + str(i.claimed_end.minute)
        cell = cell + """<tr><td>""" + "CID(" + str(id) + ") " + name + """</td><td>""" + str(
            i.shift_date) + """</td><td>""" + str(convertTime(sstart)) + '-' + str(convertTime(send)) + """<td>""" + str(
            convertTime(cstart)) + '-' + str(
            convertTime(cend)) + """</td><td>""" + """<input style='width: 100%' class="form-fan" type="time" name=""" + '"' + str(i.shift_id) + '-st' + '"' """ value="">""" + """</td><td>""" + """<input  style='width: 100%' class="form-fan" type="time" name=""" + '"' + str(i.shift_id) + '-en' + '"' """ value="">""" + """</td><td><button name="submit" class='btn btn-primary' type="submit">Save</button></td></tr>"""

    return start + cell + '<br>' + """<a class='btn btn-danger' href='/approvehours'>Cancel</a>"""


def cellmakef(ranger, shiftstore):
    infocell = ''
    w = 0
    total = 0
    for e in shiftstore:
        total = total + shiftstore[e]
    infocell = infocell + '<td>' + str(total) + '</td>'
    for g in ranger:
        w = 1
        for m in shiftstore:
            if str(g) == str(m):
                infocell = infocell + '<td>' + str(shiftstore[str(m)]) + '</td>'
                w = 0

        if w == 1:
            infocell = infocell + '<td>' + '</td>'
    return infocell


def makereport(startmonth, startyear, switch, staffname1):
    start = '''<table border='1' class='table-sm'><tr><th>Staff</th><th>Client</th><th>Department</th><th>Total Hours</th>'''
    end = '</table>'
    startl = '<tr>'
    endl = '</tr>'
    smonth = startmonth
    syear = startyear
    month = 0
    check = 0
    new = 1
    header = ''
    restaff = ''
    reclient = ''
    redep = ''
    cells = ''
    celltitle = ''
    count = 0
    count2 = 0
    infocell = ''
    outcell = ''
    searche = ''
    searchs = ''
    count1 = 0
    shiftstore = {}
    switch = switch
    endofmonth = monthrange(int(startyear), int(startmonth))

    if switch == 'half1':
        ranger = range(1, 16)
        searchs = syear + '-' + smonth + '-' + '01'
        searche = syear + '-' + smonth + '-' + '15'
        for i in ranger:
            cells = cells + '<th>' + str(i) + '</th>'
    if switch == 'full':
        ranger = range(1, endofmonth[1] + 1)
        searchs = syear + '-' + smonth + '-' + '01'
        searche = syear + '-' + smonth + '-' + str(endofmonth[1])
        for i in ranger:
            cells = cells + '<th>' + str(i) + '</th>'
    if switch == 'half2':
        ranger = range(16, endofmonth[1] + 1)
        searchs = syear + '-' + smonth + '-' + '16'
        searche = syear + '-' + smonth + '-' + str(endofmonth[1])
        for i in ranger:
            cells = cells + '<th>' + str(i) + '</th>'
    shiftnames = Shift.objects.filter(status_code='Approved', shift_date__range=(searchs, searche)).values_list('staff_id', flat=True)
    shiftnames = list(shiftnames)
    shiftnames = list(dict.fromkeys(shiftnames))
    if staffname1:
        shifts = Shift.objects.filter(status_code='Approved', staff_id=staffname1, shift_date__range=(searchs, searche)).values_list('staff_id', 'client_id')
    else:
        shifts = Shift.objects.filter(status_code='Approved', shift_date__range=(searchs, searche)).values_list('staff_id', 'client_id')
    shifts = list(shifts)
    shifts = list(dict.fromkeys(shifts))
    if len(shifts) == 0:
        return '<p> No shifts for this time period. </p>'
    for y in shifts:
        catigory = Shift.objects.filter(status_code='Approved', shift_date__range=(searchs, searche), staff_id=y[0], client_id=y[1])
        for q in catigory:
            if new == 0:
                if q.staff_id == restaff:
                    if q.client_id == reclient:
                        if q.dep_code == redep:
                            if q.shift_date.day in shiftstore:
                                shiftstore[str(q.shift_date.day)] = shiftstore[str(q.shift_date.day)] + (
                                            (q.scheduled_end.hour + (q.scheduled_end.minute / 60)) - (
                                                q.scheduled_start.hour + (q.scheduled_start.minute / 60)))
                            else:
                                shiftstore[str(q.shift_date.day)] = (
                                            (q.scheduled_end.hour + (q.scheduled_end.minute / 60)) - (
                                                q.scheduled_start.hour + (q.scheduled_start.minute / 60)))
                            continue
                        else:
                            go = cellmakef(ranger, shiftstore)
                            outcell = outcell + (startl + celltitle + go + endl)
                            infocell = ''
                            celltitle = ''
                            shiftstore.clear()
                            new = 1
                    else:
                        go = cellmakef(ranger, shiftstore)
                        outcell = outcell + (startl + celltitle + go + endl)
                        infocell = ''
                        celltitle = ''
                        shiftstore.clear()
                        new = 1
                else:
                    go = cellmakef(ranger, shiftstore)
                    outcell = outcell + (startl + celltitle + go + endl)
                    infocell = ''
                    celltitle = ''
                    shiftstore.clear()
                    new = 1
            name = Profile.objects.filter(staff_id=q.staff_id).values_list('staff_fname', 'staff_lname')
            cname = Client.objects.filter(client_id=q.client_id).values_list('client_fname', 'client_lname')
            name = list(name)
            cname = list(cname)
            top = '<td>' + 'ID(' + str(q.staff_id) + ') ' + str(name[0][0]) + ', ' + str(name[0][1]) + '</td>'
            mid = '<td>' + 'CID(' + str(q.client_id) + ') ' + str(cname[0][0]) + ', ' + str(cname[0][1]) + '</td>'
            low = '<td>' + str(q.dep_code.dep_name) + '</td>'
            celltitle = top + mid + low
            if q.shift_date.day in shiftstore:
                shiftstore[str(q.shift_date.day)] = shiftstore[str(q.shift_date.day)] + ((q.scheduled_end.hour + (q.scheduled_end.minute / 60)) - (q.scheduled_start.hour + (q.scheduled_start.minute / 60)))
                restaff = q.staff_id
                reclient = q.client_id
                redep = q.dep_code
                new = 0
            else:
                shiftstore[str(q.shift_date.day)] = ((q.scheduled_end.hour + (q.scheduled_end.minute / 60)) - (q.scheduled_start.hour + (q.scheduled_start.minute / 60)))
                restaff = q.staff_id
                reclient = q.client_id
                redep = q.dep_code
                new = 0
    go = cellmakef(ranger, shiftstore)
    outcell = outcell + (startl + celltitle + go + endl)
    infocell = ''
    celltitle = ''
    shiftstore.clear()
    new = 1
    re = [' ', ' ']
    re[0] = start + cells + endl + outcell + end
    re[1] = shiftnames
    return start + cells + endl + outcell + end


def stafflist(switch, syear, smonth):
    endofmonth = monthrange(int(syear), int(smonth))
    if switch == 'half1':
        ranger = range(1, 16)
        searchs = syear + '-' + smonth + '-' + '01'
        searche = syear + '-' + smonth + '-' + '15'
    if switch == 'full':
        ranger = range(1, endofmonth[1] + 1)
        searchs = syear + '-' + smonth + '-' + '01'
        searche = syear + '-' + smonth + '-' + str(endofmonth[1])
    if switch == 'half2':
        ranger = range(16, endofmonth[1] + 1)
        searchs = syear + '-' + smonth + '-' + '16'
        searche = syear + '-' + smonth + '-' + str(endofmonth[1])
    shiftnames = Shift.objects.filter(status_code='Approved', shift_date__range=(searchs, searche)).values_list('staff_id', flat=True)
    shiftnames = list(shiftnames)
    shiftnames = list(dict.fromkeys(shiftnames))
    return shiftnames