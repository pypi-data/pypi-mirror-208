def info():
    print("""
    from kanren import run,var,fact
    from kanren.assoccomm import eq_assoccomm as eq
    from kanren.assoccomm import commutative,associative
    add='add'
    mul='mul'
    fact(commutative,mul)
    fact(commutative,add)
    fact(commutative,mul)
    fact(commutative,add)
    a=var('a')
    b=var('b')
    pattern=(add,(mul,2,a,b),b)
    expr1=(add,(mul,2,1,2),2)
    expr2=(add,3,(mul,2,1,3))
    expr3=(add,3,(mul,2,3,1))
    print(run(0,(a,b),eq(expr1,pattern)))
    print(run(0,(a,b),eq(expr2,pattern)))
    print(run(0,(a,b),eq(expr3,pattern)))
    
    """)