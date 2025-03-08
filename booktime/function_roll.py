import info.models
from info.models import *
from users.models import Profile
from datetime import datetime, timedelta, date

# Not touching any of this code unless its shown to have errors, its probably overly complicated, but "it just works".

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


def makecalender(mperms, list, month, year):
    count2 = 0
    m = int(len(list))
    n = 3
    oop = [[0 for x in range(n)] for x in range(m)]
    for i in list:
        oop[count2][0] = str(i.scheduled_start) + '-' + str(i.scheduled_end)
        oop[count2][1] = i.shift_id
        oop[count2][2] = i.shift_date
        count2 += 1
    numdays = mperms[1]
    dayoweek = mperms[0]
    padding = 0
    endpadding = 0
    count = 1
    daymsg = ''
    calender = ''
    totaldays = 0
    count3 = 0
    nl = 0
    days = ''
    dayss = ''
    breac = 0
    end = ''
    if dayoweek != 6:
        padding = dayoweek + 1
    else:
        padding = 0
    breac = dayoweek
    totaldays = padding + numdays
    while totaldays % 7 != 0:
        endpadding += 1
        totaldays += 1
    start = '''<table class='calendar'><tr ></tr><tr><th colspan='7'><h2>''' + str(month) + ' ' + str(year) + '''</h2></th></tr><tr><th class='header'>Sunday</th><th class='header'>Monday</th><th class='header'>Tuesday</th><th class='header'>Wednesday</th><th class='header'>Thursday</th><th class='header'>Friday</th><th class='header'>Saturday</th><tr>'''
    for r in range(padding):
        calender = calender + '<td>&nbsp</td>'
    calender = start + calender
    for p in range(numdays):
        if breac == 6:
            daymsg = ''
            count3 = 0
            for n in range(numdays):
                try:
                    if str(oop[count3][2].day) == str(count):
                        daymsg = daymsg + '<a href="shiftdetails/' + str(oop[count3][1]) + '">' + str(oop[count3][0]) + '</a>'
                    count3 += 1
                except IndexError:
                    count3 += 1
            dayss = dayss + ('<td>' + str(count) + daymsg + '</td>')
            breac = 0
            count += 1
            continue
        if breac == 5:
            count3 = 0
            daymsg = ''
            for n in range(numdays):
                try:
                    if str(oop[count3][2].day) == str(count):
                        daymsg = daymsg + '<a href="shiftdetails/' + str(oop[count3][1]) + '">' + str(oop[count3][0]) + '</a>'
                    count3 += 1
                except IndexError:
                    count3 += 1
            dayss = dayss + ('<td>' + str(count) + daymsg + '</td>' + '</tr><tr>')
            breac = 6
            count += 1
            continue
        else:
            count3 = 0
            daymsg = ''
            for n in range(numdays):
                try:
                    if str(oop[count3][2].day) == str(count):
                        daymsg = daymsg + '<a href="shiftdetails/' + str(oop[count3][1]) + '">' + str(oop[count3][0]) + '</a>'
                    count3 += 1
                except IndexError:
                    False
                    count3 += 1
            dayss = dayss + ('<td>' + str(count) + daymsg + '</td>')
            breac += 1
            count += 1
    calender = calender + dayss
    for j in range(endpadding):
        end = end + '<td>&nbsp</td>'
    end = end + '</tr></table>'
    calender = calender + end

    return calender


def maketimesheet(list, today, month):
    start = '''<table class='table-sm' border='1'>'''
    end = '</table>'
    output = ''
    sheet = ''
    hocells = ''
    switch = 0
    startline = '<tr>'
    endline = '</tr>'
    gocells = ''
    count1 = 1
    day = today.day
    if day >= 16:
        count = 1
        count1 = 1
        ranger = range(15)
        cells = '''<tr><th>Individual Served</th><th>Specifics</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th></tr><tr>'''
    else:
        count = 16
        count1 = 16
        ranger = range(16, month[1] + 1)
        switch = 1
        for i in ranger:
            output = output + '<th>' + str(i) + '</th>'
    if day <= 15:
        cells = '''<tr><th>Individual Served</th><th>Specifics</th>''' + output + '''</tr><tr>'''
    sheet = start + cells
    for p in list:
        gocells = ''
        hocells = ''
        first = Client.objects.filter(client_id=p.client_id).values_list('client_fname', flat=True)
        last = Client.objects.filter(client_id=p.client_id).values_list('client_lname', flat=True)
        startcell = '<td>' + '<b>Last:</b> ' + str(last[0]) + '</td>' + '<td>Start Time:</td>'
        endcell = '<td>' + '<b>First:</b> ' + str(first[0]) + '</td>' + '<td>End Time:</td>'
        for m in ranger:
            if p.shift_date.day == count:
                gocells = gocells + """<td><input type='time' name='""" + str(p.shift_id) + """-st' value='""" + str(p.scheduled_start) + """' /></td>"""
                count += 1
            else:
                gocells = gocells + '<td></td>'
                count += 1
        for n in ranger:
            if p.shift_date.day == count1:
                hocells = hocells + """<td><input type='time' name='""" + str(p.shift_id) + """-en' value='""" + str(p.scheduled_end) + """' /></td>"""
                count1 += 1
            else:
                hocells = hocells + '<td></td>'
                count1 += 1
        gocells = startcell + gocells + endline
        hocells = endcell + hocells + endline

        sheet = sheet + gocells + hocells
    sheet = sheet + end
    return sheet




