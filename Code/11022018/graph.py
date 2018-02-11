def graph(temps,humids,mintemp,maxtemp,minhumid,maxhumid,refresh):
    # dates = matplotlib.dates.date2num(times)
    # plt.plot_date(dates, temps,'r',label='^C',marker='o')
    # plt.legend()
    # axes = plt.gca()
    # plt.draw()
    # plt.pause(refresh)
    # plt.clf()
    #
    ax1=plt.subplots()
    ax1.plot(temps,'r', marker='o')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Temperature (^C)', color='r')
    ax1.tick_params('y', colors='r')

    ax2 = ax1.twinx()
    ax2.plot(humids, 'b', marker='^')
    ax2.set_ylabel('Relative Humidity (%)',color='b')
    ax2.tick_params('y', colors='r')

#dates = matplotlib.dates.date2num(times)
#matplotlib.pyplot.plot_date(dates, temps)
