"""

"""
from functools import partialmethod

from addict import Dict as dc
from prettytable import PrettyTable
from z3 import *

# We know each queen must be in a different row.
# So, we represent each queen by a single integer: the column position


# Sorts of things we have

Day, d = EnumSort('Day', ('Mon', 'Tue', 'Wed', 'Thu', 'Fri'))
Slot, s = EnumSort('Slot', ('AM', 'PM'))
Rotation, (VA, RC, CAY, Therapy, Addiction, ECT, Sleep, Forensic, Community, didactics, off) = \
    EnumSort(
        'Rotation',
        ('VA',
         'RC',
         'CAY',
         'Therapy',
         'Addiction',
         'E_ECT',
         'E_Sleep',
         'E_Forensic',
         'E_Community',
         'didactics',
         'off'))
Resident, r = EnumSort('Resident', ('r1', 'r2', 'r3', 'r4', 'r5'))

sch = Function('schedule', Day, Slot, Resident, Rotation)

ss = Solver()


Mon, Tue, Wed, Thu, Fri = d
AM, PM = s

class NewVar():
    v = 0
    @staticmethod
    def newVar(T):
        NewVar.v
        i = Const("resVar" + str(NewVar.v), T)
        NewVar.v += 1
        return i

    new_var_res = partialmethod(newVar, Resident)



"""
Sets min and max required to complete rotation
"""


def setRotationMinMax(rotation, min, max, residentGroup=r):
    def countConditionMinMaxForRotation(resident):
        counts = []
        for i_d in d:
            for j_s in s:
                counts.append(If(sch(i_d, j_s, resident) == rotation, 1, 0))

        return And(Sum(counts) >= min, Sum(counts) <= max)

    return And(*[countConditionMinMaxForRotation(r1) for r1 in residentGroup])


"""
Sets min and max available for residents given rotation, day, slot with min and max values
"""


def setSlotMinMax(rotation, i_d, j_s, min, max):
    counts = []
    for r1 in r:
        counts.append(If(sch(i_d, j_s, r1) == rotation, 1, 0))
    c = And(Sum(counts) <= max, min <= Sum(counts), min <= max)
    return c


"""
Exactly One elective out of elective [E_Sleep, E_Forensic, E_Community, E_ECT]
"""


def onlyOneRotationOutOf(electives):
    def countRotation(resident):
        counts = []
        for i_d in d:
            for j_s in s:
                for e in electives:
                    r = sch(i_d, j_s, resident)
                    counts.append(If(r == e, 1, 0))
        return Sum(counts) == 1

    return ss.add(And(*[countRotation(r1) for r1 in r]))


"""
Makes rotation unavailable for given day and slot
"""
def turnOff(rotation, do, so):
    ro = NewVar.new_var_res()
    ss.add(setSlotMinMax(rotation, do, so, 0, 0))
    ss.add(ForAll([ro], sch(do, so, ro) != rotation))


#######################
onlyOneRotationOutOf([ECT, Forensic, Community, Sleep])


####################### VA
def setupVA():
    ROTA = VA
    ss.add(setRotationMinMax(ROTA, 1, 3))

    # VA Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Wed is off
        if i_d == Wed and i_s == PM:
            turnOff(ROTA, Wed, PM)
        else:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 3))

    return cond


############## Didactics
def setupDiadactics():
    ROTA = didactics
    ss.add(setRotationMinMax(ROTA, 1, 1))

    def cond(i_d: Day, i_s: Slot):
        if i_d == Wed and i_s == PM:
            r_len = len(r)
            ss.add(setSlotMinMax(ROTA, i_d, i_s, r_len, r_len))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


################ off
ss.add(setRotationMinMax(off, 1, 1))
r_off = NewVar.new_var_res()
# Try to give friday off
# ss.add(ForAll([r_off], Or(sch(Fri, AM, r_off) == off, sch(Fri, PM, r_off) == off)))

# Try to offer Friday Afternoon off
ss.add(ForAll([r_off], Or(sch(Fri, PM, r_off) == off)))


# If resident has friday morning OFF, select RC for evening
# ss.add(ForAll([r_off], If(sch(Fri, PM, r_off) == RC, sch(Fri, AM, r_off) == off, True)))


################## RC
def setupRC():
    ROTA = RC
    ss.add(setRotationMinMax(ROTA, 2, 3))

    # # RC Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Wed is off
        if i_d == Wed and i_s == PM:
            turnOff(ROTA, Wed, PM)
        else:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 3))

    return cond


#################### CAY

def setupCAY():
    ROTA = CAY
    # Custom Condition:
    # Four residents with CAY Clinic

    ss.add(setRotationMinMax(ROTA, 1, 1, r[:4]))
    ss.add(setRotationMinMax(ROTA, 0, 1, r[4:]))

    # CAY Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if (i_d == Tue or i_d == Thu) and i_s == PM:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 2, 2))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


####################### Therapy
def setupTherapy():
    ROTA = Therapy
    ss.add(setRotationMinMax(ROTA, 1, 1))

    # VA Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Wed is off
        if i_d == Wed and i_s == PM:
            turnOff(ROTA, Wed, PM)
        else:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 2))

    return cond


##################### Addiction
def setupAddiction():
    ROTA = Addiction
    # ss.add(setRotationMinMax(ROTA, 0, 1))

    # Four residents with CAY Clinic
    ss.add(setRotationMinMax(ROTA, 1, 1, r[:4]))
    ss.add(setRotationMinMax(ROTA, 0, 1, r[4:]))

    # Addiction Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if i_d == Tue:
            ss.add(setSlotMinMax(ROTA, i_d, AM, 1, 2))
            ss.add(setSlotMinMax(ROTA, i_d, PM, 1, 3))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


######################### ECT
def setupECT():
    ROTA = ECT
    ss.add(setRotationMinMax(ROTA, 0, 1))

    # Addiction Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if i_d in [Mon, Wed, Fri] and i_s == AM:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 1))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


######################### Sleep
def setupSleep():
    ROTA = Sleep
    ss.add(setRotationMinMax(ROTA, 0, 1))

    # Addiction Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if i_d in [Tue, Thu] and i_s == AM:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 1))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


######################### Forensic
def setupForensic():
    ROTA = Forensic
    ss.add(setRotationMinMax(ROTA, 0, 1))

    # Addiction Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if i_s == AM:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 1))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


######################### Community
def setupCommunity():
    ROTA = Community
    ss.add(setRotationMinMax(ROTA, 0, 1))

    # Addiction Slot Min Max:
    def cond(i_d: Day, i_s: Slot):
        # Enabled on Tue or Thu evening
        if i_s == AM:
            ss.add(setSlotMinMax(ROTA, i_d, i_s, 0, 1))
        else:
            turnOff(ROTA, i_d, i_s)

    return cond


# All Conditions
cnd = [
    setupVA(),
    setupDiadactics(),
    setupRC(),
    setupAddiction(),
    setupECT(),
    setupSleep(),
    setupTherapy(),
    setupCAY(),
    setupCommunity(),
    setupForensic()
]

# Add Conditions
for i_d in d:
    for i_s in s:
        for f in cnd:
            f(i_d, i_s)


def get_counters(model):
    all = []
    raw_data = []
    govinda = [["Resident", "Slot"] + [str(di) for di in d]]

    for r1 in r:
        for i_s in s:
            govinda_slot = [str(r1), str(i_s)]
            for i_d in d:
                rt = model.evaluate(sch(i_d, i_s, r1))
                govinda_slot.append(str(rt))
                all.append(dc({"ro": rt, "d": i_d, "s": i_s, "r": r1}))
                raw_data.append([str(i_d), str(i_s), str(r1), str(rt)])
            govinda.append(govinda_slot)

    counter_by_rotation = dc()

    for row in all:
        ro = row['ro']
        dd = row['d']
        ss = row['s']
        counter_by_rotation[ro][dd][ss] += 1

    counter_by_resident = dc()

    for row in all:
        re = row['r']
        ro = row['ro']
        counter_by_resident[re][ro] += 1

    #     print(counter_by_rotation)
    #     print(counter_by_resident)
    return counter_by_rotation, counter_by_resident, raw_data, govinda


def print_rotation(counter_by_rotation):
    for ro, ro_val in counter_by_rotation.items():
        x = PrettyTable()
        x.title = f"{ro} Schedule"
        # x.field_names = [str(d_day.name) for d_day in d]
        x.add_column("Slot", ["AM", "PM"])
        for i_d in d:
            # for dd, dd_val in ro_val.items():
            mm = ["--", "--"]
            for v in ro_val.get(i_d, {}):
                v_val = ro_val[i_d][v]
                if v == AM:
                    mm[0] = str(v_val)
                else:
                    mm[1] = str(v_val)
            x.add_column(str(i_d), mm)
        print(x)


def print_resident_schedule(resident, model):
    x = PrettyTable()
    x.title = f"{resident} Schedule"
    x.add_column("Slot", ["AM", "PM"])

    for i_d in d:
        mm = []
        for j_s in s:
            r = model.evaluate(sch(i_d, j_s, resident))
            mm.append(str(r))
        x.add_column(str(i_d), mm)
    print(x)


def print_resident_summary(resident, counter_by_resident):
    values = counter_by_resident.get(resident)
    print(f"Summary for {resident=}: {values=}")
    print("-------------------     xxxxxxxxx -------------------------")
    return


def store_csv(raw_data, fname):
    import csv

    with open(fname, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerows(raw_data)


if __name__ == '__main__':
    print(ss.check())
    model = ss.model()
    # print(model)

    counter_by_rotation, counter_by_resident, raw_data, govinda = get_counters(model)

    # counter_by_rotation, counter_by_resident = get_counters(model)
    for r1 in r:
        print_resident_schedule(r1, model)
        print_resident_summary(r1, counter_by_resident)

    print_rotation(counter_by_rotation)
    store_csv(raw_data, 'schedule-pgy3-2022-23.csv')
    store_csv(govinda, 'schedule-govinda-pgy3-2022-23.csv')
