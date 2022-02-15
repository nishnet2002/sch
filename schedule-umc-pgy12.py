"""

"""
from addict import Dict as dc
from z3 import *
from prettytable import PrettyTable

year = 22
Month, m = EnumSort('Month', ('July-22', 'Aug-22', 'Sep-22', 'Oct-22', 'Nov-22', 'Dec-22', 'Jan-23', 'Feb-23', 'Mar-23', 'Apr-23', 'May-23', 'Jun-23'))
Rotation, (VA3L, ER, Neuro, Outpatient, HouseMedicine, _7E, _7W, PES_AM, PES_PM, Consult, Child, Geriatrics, Addiction, Elective) = \
    EnumSort(
        'Rotation',
        ('VA-3L',
         'ER',
         'Neuro',
         'Outpatient',
         'HouseMedicine',
         '7E',
         '7W',
         'PES-AM',
         'PES-PM',
         'Consult',
         'Child',
         'Geriatrics',
         'Addiction',
         'Elective'
         ))
Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun = m
strPGY1 = ['PGY1-1', 'PGY1-2', 'PGY1-3', 'PGY1-4', 'PGY1-5', 'PGY1-6', 'PGY1-7', 'PGY1-8', 'PGY1-9']
strPGY2 = ['PGY2-1', 'PGY2-2', 'PGY2-3', 'PGY2-4', 'PGY2-5', 'PGY2-6', 'PGY2-7', 'PGY2-8']
allResidentStr = tuple(strPGY1 + strPGY2)
print(allResidentStr)
Resident1, r = EnumSort('Resident1', allResidentStr)


pgy1 = r[:len(strPGY1)]
pgy2 = r[len(strPGY1):]

# Avoid these hectic rotations in succession
hectic_rotations = {PES_AM, PES_PM, HouseMedicine, ER}

# Schedule data model
sch = Function('schedule', Month, Resident1, Rotation)
ss = Solver()
v = 0


"""
Sets min and max required to complete rotation
"""
def setRotationMinMax(residentsGroup, rotation, min, max):
    assert (min <= max)
    def countConditionMinMaxForRotation(resident):
        counts = []
        for mi in m:
            counts.append(If(sch(mi, resident) == rotation, 1, 0))
        return And(Sum(counts) >= min, Sum(counts) <= max)
    return And(*[countConditionMinMaxForRotation(r1) for r1 in residentsGroup])


"""
Sets min and max available for residents given rotation, day, slot with min and max values
"""
def setSlotMinMax(residentsGroup, rotation, month, min, max):
    assert(min <= max)
    counts = [If(sch(month, res) == rotation, 1, 0) for res in residentsGroup]
    return And(Sum(counts) >= min, Sum(counts) <= max)

"""
Makes rotation unavailable for given month
"""
def turnOff(residentGroup, rotation, mo):
    ss.add(setSlotMinMax(residentGroup, rotation, mo, 0, 0))
    for r_idx in residentGroup:
        ss.add(sch(mo, r_idx) != rotation)

"""
Hectic rotations should not repeat in succession
"""
def removeAdjDuplicateRotations():
    cond = []
    for r1 in r:
        for mi in range(1, len(m)):
            ro_m0 = sch(m[mi - 1], r1)
            ro_m1 = sch(m[mi], r1)
            hectic_cond = []
            for r_hectic in hectic_rotations:
                hectic_cond.append(If(Or(r_hectic == ro_m0, r_hectic == ro_m1), 1, 0))
            cond.append(And(ro_m0 != ro_m1, Sum(hectic_cond) < 2))
    ss.add(cond)



"""
    Rotation: VA-3L
    Capacity: 1, 2
    PGY1: 0, 1
    PGY2: 0, 1
"""
####################### VA-3L
def setupVA3L():
    ROTA = VA3L
    ss.add(setRotationMinMax(r, ROTA, 0, 2)) # TODO Rever to 0,1?

    def fn(mo):
        ss.add(setSlotMinMax(r, ROTA, mo, 1, 2))
        turnOff(pgy2, ROTA, mo)
    return fn

"""
    Rotation: ER
    Capacity: 0, 2
    PGY1: 1
    PGY2: 0
"""
####################### ER
def setupER():
    ROTA = ER
    ss.add(setRotationMinMax(pgy1, ROTA, 1, 1))
    ss.add(setRotationMinMax(pgy2, ROTA, 0, 0))

    def fn(mo):
        ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 2))
        turnOff(pgy2, ROTA, mo)
    return fn


"""
    Rotation: Neuro
    Capacity: 0, 2
    PGY1: 2
    PGY2: 0
"""
####################### Neuro
def setupNeuro():
    ROTA = Neuro
    ss.add(setRotationMinMax(pgy1, ROTA, 2, 2))
    ss.add(setRotationMinMax(pgy2, ROTA, 0, 0))

    def fn(mo):
        ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 2))
        turnOff(pgy2, ROTA, mo)
    return fn

"""
    Rotation: Outpatient
    Capacity: 0, 2
    PGY1: 2
    PGY2: 0
"""
####################### Outpatient
def setupOutpatient():
    ROTA = Outpatient
    ss.add(setRotationMinMax(pgy1, ROTA, 2, 2))
    ss.add(setRotationMinMax(pgy2, ROTA, 0, 0))

    def fn(mo):
        ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 2))
        turnOff(pgy2, ROTA, mo)
    return fn

####################### HouseMedicine
"""
    Rotation: HouseMedicine
    Capacity: 0, 2
    PGY1: 1
    PGY2: 0
"""
def setupHouseMedicine():
    ROTA = HouseMedicine
    ss.add(setRotationMinMax(pgy1, ROTA, 1, 1))
    ss.add(setRotationMinMax(pgy2, ROTA, 0, 0))
    def fn(mo):
        ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 2))
        turnOff(pgy2, ROTA, mo)
    return fn

####################### 7E
"""
    Rotation: 7E
    Capacity: 1, 2
    PGY1: 1, 3
    PGY2: 1, 3
"""
def setup_7E():
    ROTA = _7E
    ss.add(setRotationMinMax(r, ROTA, 1, 3))
    def fn(mo):
        ss.add(setSlotMinMax(r, ROTA, mo, 1, 2))
    return fn

####################### 7W
"""
    Rotation: 7W
    Capacity: 2
    PGY1: 1, 3
    PGY2: 1, 3
"""
def setup_7W():
    ROTA = _7W
    ss.add(setRotationMinMax(r, ROTA, 1, 3))
    def fn(mo):
        ss.add(setSlotMinMax(r, ROTA, mo, 2, 2))
    return fn

####################### PES_AM
"""
    Rotation: PES_AM
    Capacity: 1
    PGY1: 1, 2
    PGY2: 0, 1
"""

def setup_PES_AM():
    ROTA = PES_AM
    ss.add(setRotationMinMax(pgy1, ROTA, 1, 2))
    ss.add(setRotationMinMax(pgy2, ROTA, 0, 1))
    def fn(mo):
        ss.add(setSlotMinMax(pgy1, ROTA, mo, 1, 1))
        turnOff(pgy2, ROTA, mo)
    return fn

####################### PES_PM
"""
    Rotation: PES_PM
    Capacity: 1
    PGY1: 0
    PGY2: 1, 2
"""
def setup_PES_PM():
    ROTA = PES_PM
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 0))
    ss.add(setRotationMinMax(pgy2, ROTA, 1, 2))

    def fn(mo):
        turnOff(pgy1, ROTA, mo)
        ss.add(setSlotMinMax(pgy2, ROTA, mo, 1, 1))
    return fn

####################### Consult
"""
    Rotation: Consult
    Capacity: 2 (atleast 1 pgy2, prefer pgy1 after march)
    PGY1: 0 (after march can have 0, 1)
    PGY2: 2
"""
def setupConsult():
    ROTA = Consult
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 1))
    ss.add(setRotationMinMax(pgy2, ROTA, 2, 3))


    def fn(mo):
        # capacity exactly 2 residents
        ss.add(setSlotMinMax(r, ROTA, mo, 2, 2))

        if m.index(mo) >= m.index(Nov):
            ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 1))
            ss.add(setSlotMinMax(pgy2, ROTA, mo, 1, 2))
        else:
            turnOff(pgy1, ROTA, mo)
            ss.add(setSlotMinMax(pgy2, ROTA, mo, 2, 2))
    return fn

"""
    Rotation: Child
    Capacity: 2 (atleast 1 pgy2, prefer pgy1 only after march)

    Rotation Requirement:
    PGY1: 0;
    PGY2: 1, 2; Must have atleast 1 PGY2 at all times
"""
####################### Child
def setupChild():
    ROTA = Child
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 1))
    ss.add(setRotationMinMax(pgy2, ROTA, 2, 3))


    def fn(mo):
        # capacity exactly 2 residents
        ss.add(setSlotMinMax(r, ROTA, mo, 2, 2))

        if m.index(mo) >= m.index(Nov):
            ss.add(setSlotMinMax(pgy1, ROTA, mo, 0, 1))
            ss.add(setSlotMinMax(pgy2, ROTA, mo, 1, 2))

        else:
            turnOff(pgy1, ROTA, mo)
            ss.add(setSlotMinMax(pgy2, ROTA, mo, 2, 2))

    return fn

####################### Geriatrics
"""
    Rotation: Geriatrics
    Capacity: 0, 1
    PGY1: 0
    PGY2: 1
"""

def setupGeriatrics():
    ROTA = Geriatrics
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 0))
    ss.add(setRotationMinMax(pgy2, ROTA, 1, 1))

    def fn(mo):
        ss.add(setSlotMinMax(pgy2, ROTA, mo, 0, 1))
        turnOff(pgy1, ROTA, mo)
    return fn

####################### Addiction
"""
    Rotation: Addiction
    Capacity: 0, 1
    PGY1: 0
    PGY2: 1
"""
def setupAddiction():

    ROTA = Addiction
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 0))
    ss.add(setRotationMinMax(pgy2, ROTA, 1, 1))

    def fn(mo):
        ss.add(setSlotMinMax(pgy2, ROTA, mo, 0, 1))
        turnOff(pgy1, ROTA, mo)
    return fn

####################### Elective
"""
    Rotation: Elective
    Capacity: 0, 6
    PGY1: 0
    PGY2: 1
"""
def setupElective():
    ROTA = Elective
    ss.add(setRotationMinMax(pgy1, ROTA, 0, 0))
    ss.add(setRotationMinMax(pgy2, ROTA, 1, 1))
    def fn(mo):
        ss.add(setSlotMinMax(pgy2, ROTA, mo, 0, 6))
        turnOff(pgy1, ROTA, mo)
    return fn

##################################
#######  Custom Condition    #####

def setupCustomCondition():
    #### Custom Condiction
    # r6 Sep-22 != PES-AM
    #ss.add(sch(m[2], r[5]) != PES_AM)
    pass


# All Conditions
cnd = [
    setupVA3L(),
    setupER(),
    setupNeuro(),
    setupOutpatient(),
    setupHouseMedicine(),
    setup_7E(),
    setup_7W(),
    setup_PES_AM(),
    setup_PES_PM(),
    setupConsult(),
    setupChild(),
    setupGeriatrics(),
    setupAddiction(),
    setupElective()
]

# Add Conditions
for f in cnd:
    for mi in m:
        f(mi)


def get_counters(model):
    ################# Capture raw_data, all data in csv, and govinda data
    raw_data = []
    all = []
    # CSV First Row of (Resident, Months -->)
    govinda = [["Resident"] + [str(m1) for m1 in m]]
    for r1 in r:
        # local variable: name of resident
        govinda_rotation = [str(r1)]

        for mi in m:
            # get rotation for given month, resident
            rt = model.evaluate(sch(mi, r1))

            # capture all 3 data sets
            all.append(dc({"ro": rt, "m" : mi, "r" : r1}))
            raw_data.append([str(mi), str(r1), str(rt)])
            govinda_rotation.append(str(rt))
        govinda.append(govinda_rotation)

    ######### Generate Counter by Rotations
    counter_by_rotation = dc()
    for row in all:
        ro = row['ro']
        mm = row['m']
        counter_by_rotation[ro][mm] += 1

    ######### Generate Counter by Rotations
    counter_by_resident = dc()
    for row in all:
        re = row['r']
        ro = row['ro']
        counter_by_resident[re][ro] += 1

    return counter_by_rotation, counter_by_resident, raw_data, govinda

def print_rotation(counter_by_rotation):
    for ro, ro_val in counter_by_rotation.items():
        x = PrettyTable()
        x.title = f"{ro} Schedule"
        for mm, mm_val in ro_val.items():
            x.add_column(str(mm), [str(mm_val)])
        print(x)

def print_resident_schedule(model, resident):
    x = PrettyTable()
    x.title = f"{resident} Schedule"

    for mi in m:
        rotation = model.evaluate(sch(mi, resident))
        x.add_column(str(mi), [str(rotation)])
    print(x)

def print_resident_summary(resident, counter_by_resident):
    values = counter_by_resident.get(resident)
    l = list(values.items())
    l.sort(key = lambda x: str(x[0]))

    print(f"Summary for {resident=}: values={l}")
    print("-------------------     xxxxxxxxx -------------------------")
    return

def store_csv(raw_data, fname):
    import csv

    with open(fname, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerows(raw_data)


if __name__ == '__main__':
    setupCustomCondition()
    removeAdjDuplicateRotations()
    print (ss.check())
    model = ss.model()
    print (model)

    counter_by_rotation, counter_by_resident, raw_data, govinda = get_counters(model)
    for r1 in r:
        print_resident_schedule(model, r1)
        print_resident_summary(r1, counter_by_resident)

    store_csv(raw_data, 'schedule-pgy1,2-2022-23.csv')
    store_csv(govinda, 'schedule-govinda-pgy1,2-2022-23.csv')
    print_rotation(counter_by_rotation)

class PrinterWriter():
    def store_csv(raw_data, fname):
        import csv

        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel')
            writer.writerows(raw_data)

