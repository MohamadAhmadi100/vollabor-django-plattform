import math


# import numpy as np

def calculate_ResponsiveFee(fund, spiritual):
    total = spiritual + fund;

    # Coeff=[Main_dsupervisor,advisor,mentor,member,learner]
    Coeff = [0.50, 0.35, 0.30, 0.25, 0.10];

    efficiency = [90, 80, 70, 70, 25];

    if fund > 0:
        Resfee = []
        for ii in range(0, len(Coeff)):
            currentResfee = (1 + (0.75 * (fund / spiritual))) * Coeff[ii] * efficiency[ii] * math.log(total) / 100
            Resfee.append(currentResfee);

        # Resfee = np.array(Resfee)
        percentage = 100 * sum(Resfee) / total;

        perfund = 100 * sum(Resfee) / fund;

        FinalResFee = []
        FinalResFee.append(fund)
        FinalResFee.append(spiritual)
        FinalResFee.append(fund + spiritual)

        for ii in range(0, len(Coeff)):
            FinalResFee.append(int(round(Resfee[ii] * 100)))

        FinalResFee.append(percentage)
        FinalResFee.append(perfund)



    #     FinalResFee = [fund, spiritual, fund+spiritual, math.round(Resfee*100), percentage, perfund];

    else:
        Resfee = []
        for ii in range(0, len(Coeff)):
            currentResfee = Coeff[ii] * efficiency[ii] * math.log(spiritual)
            Resfee.append(currentResfee);

        # Resfee = np.array(Resfee)

        FinalResFee = []
        FinalResFee.append(fund)
        FinalResFee.append(spiritual)
        FinalResFee.append(fund + spiritual)

        for ii in range(0, len(Coeff)):
            FinalResFee.append(int(round(Resfee[ii])))

        FinalResFee.append(sum(Resfee) / spiritual)
        FinalResFee.append(0)

    #     FinalResFee = [fund, spiritual, fund+spiritual, np.round(Resfee), np.sum(Resfee)/spiritual, 0];
    return FinalResFee


# example

# [fund, spiritual, total , Main_dsupervisor,advisor,mentor,member, learner, percentage, perfund] = calculate_ResponsiveFee(fund,spiritual)
