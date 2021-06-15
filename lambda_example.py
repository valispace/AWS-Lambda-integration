import json
import valispace
from gekko import GEKKO
import numpy as np

# Electric vehicle model (https://nl.mathworks.com/matlabcentral/fileexchange/16613-electric-vehicle-model)
# Created by John Hedengren, john_hedengren@hotmail.com
# Based on dc motor model
# by Roger Aarenstrup, roger.aarenstrup@mathworks.com

valid_vars = ["i", "dth_m", "th_m", "dth_l", "th_l", "dth_v", "th_v"]
# i : input voltage to the motor (volts)
# dth_m: motor resistance (ohm)
# th_m : motor inductance (henrys)
# dth_l: back emf constant (volt-sec/rad)
# th_l : torque constant (N-m/a)
# dth_v: rotor inertia (kg m^2)
# th_v : mechanical damping (linear model of friction: bm * dth)

input_valis = {
    "v" : 24542,
    "rm": 24543,
    "lm": 24544,
    "jm": 24547,
    "bm": 24548,
    "jl": 24549,
    "bl": 24550,
    "b": 24552,
    "k": 24551,
    "rl": 24553
}
output_valis = {
    "i": 24555, 
    "dth_m":24556,
    "dth_l":24557,
    "dth_v":24558, 
    "th_v" :24559
}
def login():
    return valispace.API(url='https://example.valispace.com/', username = 'foo', password='bar.')

def fetch_input_valis(vs_instance):
    values= {}
    for input in input_valis:
        vali = vs_instance.request('GET', f'vali/{input_valis[input]}')
        values[input] = vali["value"]

    return values

def push_output_values(vs_instance, results):
    for output in output_valis:
        vs_instance.update_vali(id=output_valis[output], formula= results[output])
        #vs_instance.request('PATCH', f'vali/{output_valis[output]}', data={"formula"= results[output]})

def lambda_handler(event, context):
    # add extra filters here so only relevant hooks can trigger the calculations
    vali = login()
    inputs = fetch_input_valis(vali)
    res = solve_elecar(inputs=inputs, t_interval=200)
    push_output_values(vali,res)

    return {
        "statusCode": 200,
        "headers": {},
        "body": "",
        "isBase64Encoded": False
    }



def solve_elecar(inputs, t_interval=10):
    m = GEKKO()

    #Parameters

    v = m.Param(value=inputs['v']) # input voltage to the motor (volts)
    rm = m.Param(value=inputs['rm']) # motor resistance (ohm)
    lm = m.Param(value=inputs['lm']) # motor inductance (henrys)
    kb = m.Param(value=6.5e-4) # back emf constant (volt-sec/rad)
    kt = m.Param(value=0.1) # torque constant (N-m/a)
    jm = m.Param(value=inputs['jm']) # rotor inertia (kg m^2)
    bm = m.Param(value=inputs['bm']) # mechanical damping (linear model of friction: bm * dth)


    # automobile parameters
    jl =m.Param(value= inputs['jl']) # vehicle inertia (1000 times the rotor)
    bl = m.Param(value=inputs['bl']) # vehicle damping (friction)
    k = m.Param(value=inputs['k'] ) # spring constant for connection rotor/drive shaft
    b = m.Param(value=inputs['b'] ) # spring damping for connection rotor/drive shaft
    rl = m.Param(value=inputs['rl']) # gearing ratio between motor and tire (meters travelled per radian of motor rotation)
    tau = m.Param(value=2 ) # time constant of a lag between motor torque and car velocity. this lag is a simplified model of the power train. (sec)


    i = m.Var(value=0) # motor electrical current (amps)
    dth_m = m.Var(value=0) # rotor angular velocity sometimes called omega (radians/sec)
    th_m = m.Var(value=0) # rotor angle, theta (radians)
    dth_l = m.Var(value=0 ) # wheel angular velocity (rad/sec)
    th_l = m.Var(value=0 ) # wheel angle (radians)
    dth_v = m.Var(value=0) # vehicle velocity (m/sec)
    th_v = m.Var(value=0) # distance travelled (m)

    m.time = np.linspace(0,t_interval,100)

    m.Equation(lm*i.dt() - v == -rm*i - kb*th_m.dt())
    m.Equation(jm*dth_m.dt() == kt*i - (bm+b)*th_m.dt() - k*th_m + b *th_l.dt() + k*th_l)
    m.Equation(jl*dth_l.dt() == b *th_m.dt() + k*th_m - (b+bl)*th_l.dt()- k*th_l)
    m.Equation(tau * dth_v.dt() == rl * dth_l - dth_v)
    m.Equation(dth_m == th_m.dt())
    m.Equation(dth_l == th_l.dt())
    m.Equation(dth_v == th_v.dt())

    m.options.IMODE = 4
    m.solve(disp=False)

    res_dict = {}
    for var in valid_vars:
        res_dict[var] = eval(var).value[-1]
        res_dict["t"] = m.time

    return res_dict









