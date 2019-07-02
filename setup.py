from setuptools import setup

setup(
    name="demo_oc6",
    version='1.0',
    py_modules=['demo_oc6'],
    author="Jerome Lanteri",
    description='demonstrtion for OpenclassRooms project 6',
    long_description='''
        --  D e m o n s t r a t i o n  -- 
        From sql requests contained inside a xml file,
        insert records to "oc-pizza" database tables
        -- OpenClassRooms Python Path: project 6 --''',
    install_requires=["Click", "pillow", "psycopg2"],
    entry_points='''
        [console_scripts]
        demo_oc6=demo_oc6:cli
    ''',
)

