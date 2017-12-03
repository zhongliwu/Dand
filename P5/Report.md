# OpenStreetMap Data Case Study

**Author: Laurence Wu**

**Date: Nov 24, 2017**


## Map Area

[Sydney, Australia](https://en.wikipedia.org/wiki/Sydney)
* Dateset: https://mapzen.com/data/metro-extracts/metro/sydney_australia/

This is a great metropolitan area in the Southern Hemisphere. Immigrants from all over the world are living together in this city. It makes me remember San Francisco in the United States, the immigration city where I worked for half a year.

## Problems encountered in the dataset

The dateset is as large as 223 MB. After I use code in grab_example.py to grab 20.5 MB sample data, I found those fields have problems. I will discuss them in the following order:

+ Unformed phone numbers. ("(02) 9878 5559", "+61 2 92625491", "0291305063")

+ State code not used correctly. ("New South Wales", "NSW")

+ Inconsistent postcode. ("2???", "NSW 2010", "2048")

### **Unformed phone numbers**

From the sample dataset, I saw a lot of problems with phone numbers. 
First, some of the numbers do not contains area code. Likewise, some phone numbers do not have spaces to make the phone number readable. Examples might be: "(02) 9889 7770", "99771029"

Local calls numbers, like 1300, are included in this dataset. "1300 885 588"

I also noticed some area have more than one phone number and they use semicolon to seperate different numbers. So I will seperate those fields using semicolon, format each of the phone number and merge them again after cleaning.

From the Google Map location description, I decided to format all the numbers into the international form: +61 2 XXXX XXXX and eliminate phone numbers with local calls numbers. I will use the following code to clean the phone number field:

```python
PHONENUM = re.compile(r'\+61\s2\s\d{4}\s\d{4}')

def cleanPhoneData(phone_field):
    phone_num_list = phone_field.split(";")
    audit_phone_num = ''

    for phone_num in phone_num_list:
        m = PHONENUM.match(phone_num)
        if m is None:
            # convert all dashes ("-") to spaces
            if "-" in phone_num:
                phone_num = re.sub("-", " ", phone_num)
            # convert all parenthesis to spaces
            if "(" in phone_num or ")" in phone_num:
                phone_num = re.sub("[()]", "", phone_num)
            # remove all + at the first
            phone_num = re.sub("\+", "", phone_num)

            # Remove all 61 at the first
            if phone_num.startswith("61") is True:
                phone_num = phone_num[2:].strip()

            # ignore local call numbers
            if phone_num.startswith("1300 ") or 
                phone_num.startswith("1300") is True:
                pass
            # remove '2' or '02'
            elif phone_num.startswith("2") is True:
                phone_num = phone_num[1:].strip()
            elif phone_num.startswith("02") is True:
                phone_num = phone_num[2:].strip()
            
            # now start to clean the format
            if sum(n.isdigit() for n in phone_num) != 8:
                phone_num = None
            elif re.match(r'^\d{8}$', phone_num) is not None:
                phone_num = phone_num[:4] + " " + phone_num[4:]
            elif re.match(r'^\d{4}\s\d{4}$', phone_num) is not None:
                pass
            else:
                re.sub('\s', '', phone_num)
                phone_num = phone_num[:4] + " " + phone_num[4:]

        if phone_num is not None:
            if m is None:
                # after cleaning, re-add "+61 2 " prefix
                phone_num = "+61 2 " + phone_num
            
            if len(audit_phone_num) == 0:
                audit_phone_num = phone_num
            else:
                audit_phone_num = audit_phone_num + ";" + phone_num

    if audit_phone_num == '':
        return None
    else:
        return audit_phone_num

```

### **State code not used**
 Some of the state code are not abbreviated. They are "New South Wales"instead of "NSW" as they should be. I will use the following code to convert them to the correct format.

```python
def cleanStateName(state_name):
    if (state_name == 'New South Wales'):
        state_name = 'NSW'
    
    return state_name
```

### **Inconsistent postcode**

Some postcodes contains state name, like "NSW 2010". The prefix "NSW" should be removed. During the cleaning process, I also found one postcode is "2???". This might be due to typos or system errors. I will simply skip this data.
```python
def cleanPostCode(postcode):
    if postcode.startswith('NSW') is True:
        postcode = postcode[3:].strip()
    
    matcher = re.search(POSTCODEPROBLEM, postcode)
    if matcher is not None:
        postcode = None

    return postcode
```
The above code is used to wrangle postcode. The regular expression, "POSECODEPROBLEM", filter problematic characters like '?' and EOL. Once it finds those chars, a None will be returned in this function.



## Date Overview
This section contains basic statistics about the Sydney OpenStreetMap dataset, the SQL queries used to gather them, and some additional ideas about the data in context.


**File Sizes**

```
sydney_australia.osm ..... 332.1 MB
sydney.db ................ 183.5 MB
nodes.csv ................ 122.4 MB
nodes_tags.csv ...........   6.2 MB
ways.csv .................    12 MB
ways_tags.csv ............    23 MB
ways_nodes.csv ...........  42.2 MB
```

**Number of Nodes**

```sql
sqlite> SELECT COUNT(*) AS NUM_OF_NODES FROM NODES;
```
1474183


**Number of Ways**
```sql
sqlite> SELECT COUNT(*) AS NUM_OF_WAYS FROM WAYS;
```
202420

**Number of Unique Users**
```sql
sqlite> SELECT COUNT(DISTINCT(E.UID)) AS NUM_OF_UNIQUE_USERS 
FROM (SELECT UID FROM NODES UNION ALL SELECT UID FROM WAYS) E;
```
2300

**create a view from nodes and ways for easily selecting**
```sql
sqlite> CREATE VIEW CONTRIBUTORS AS 
SELECT USER, TIMESTAMP, UID FROM NODES UNION ALL 
SELECT USER, TIMESTAMP, UID FROM WAYS;
```

**Top 10 contributing users**
```sql
sqlite> SELECT COUNT(*) AS NUM_OF_CONTRIBUTION, USER 
FROM CONTRIBUTORS GROUP BY USER 
ORDER BY NUM_OF_CONTRIBUTION DESC 
LIMIT 10;
```
117376|balcoath\
89558|inas\
74756|TheSwavu\
65300|aharvey\
60739|ChopStiR\
48305|Leon K\
48182|ozhiker2\
42045|cleary\
40847|Rhubarb\
37584|AntBurnett

**Latest Contribution**
```sql
sqlite> SELECT * FROM CONTRIBUTORS ORDER BY TIMESTAMP DESC LIMIT 1;
```
TuanIfan|2017-11-19T12:56:07Z

**Top 10 popular cuisines**
```sql
select count(*) as num, value from (select key, value from nodes_tags union all select key, value from ways_tags) where key='cuisine' group by value order by num desc limit 10;
```
163|burger
118|coffee_shop
116|pizza
93|chicken
87|thai
67|chinese
66|italian
49|japanese
49|sandwich
43|indian


**Number of ways with surface attribute**
```sql
sqlite> SELECT count(*) FROM WAYS_TAGS WHERE KEY='surface';
```
26012

**Number of ways that is a building**
```sql
sqlite> SELECT count(*) FROM WAYS_TAGS WHERE KEY='building';
```
40110


## Dateset improvement

Some of the queries above shows some statistics about the dataset. The number of ways is 202420, while the number of ways with surface attribute is 26012. If the ways tag is a building, it might not need a 'surface' attribute. So the proportion of ways with sufficient 'suface' attribute is 26012 / 202420 = 0.129. This is a pretty low number, as every street/building has their own material, this number is expected to be 100%. 

#### Solution: Encourage every contributor in OpenStreetMap to provide the surface attribute when contributing data. Offer great prize for the top contributors.
+ Pros:
    1. The 'great prize' will attract even a lot of new users to come and contribute to the dataset.
    2. Contributors will spend time in contributing the material attribute, this can highly improve the proportion of way tags with 'surface' attribute
+ Cons:
    1. The contributors might be unable to recognize the material either for a way or for a buiding. They are most likely to add fake 'material' attribute to their way tags in order to give more 'contribution' to the dataset.
    2. It takes time to modify the program to identify which contributor contribute most number of the 'surface' attribute.


# Conclusion

The Sydney OpenStreetMap data is not quite large, but it's actually in a mess. After my cleaning of this dataset, we can get well-format phone number, postcodes, state code, although it's not 100% ensured. Throught the SQL queries, I learned something for the city. Like the most popular cuisine is a burger restaurant. I also learned how the dataset can be insufficient when some attributes (in this case, the 'surface' attribute) are missing from the dataset.