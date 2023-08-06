def btrinpt(type,user_inpt_display,numberofelements):
    k=str(user_inpt_display)
    n=int(numberofelements)
    global mylist
    mylist=[]   
    for i in range(0,n):
        ic=str(i)
        kf=str(k+ic+":")
        if type=="str":
            xu=str(input(kf))
            mylist.append(xu)
        elif type == "int":
            xu=int(input(kf))
            mylist.append(xu)
        elif type=="mixed":
            subtypetext=str(kf+"is this str or int, reply s/i:")
            subtype=str(input(subtypetext))
            if subtype=="s":
                xu=str((input(kf)))
                mylist.append(xu)
            if subtype=="i":
             xu=int(input(kf))
             mylist.append(xu)
        else:
            xu=(input(kf))
            mylist.append(xu)
    return mylist

