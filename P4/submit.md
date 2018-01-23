# A/B Testing Analysis Report

> Author: Laurence Wu
Date: 01/21/2018


### Experiment Design

#### Metric Choice

For each metric, I evaluated them as below:

+ *Number of cookies: That is, number of unique cookies to view thecourse overview page.* This metric will definitely stay the same before and afer the invervention.
+ *Number of user­ ids: That is, number of users who enroll in the freetrial.* The hint windows appears after the user clicks the 'start free trial' button. This will have an impact on the user's decision about whether to join in the class. This metric can't be used as the invariant metric. On the other part, the number of userids will be influenced by the number of users who visit the udacity website or the number of users who visit the course. These statistics might be different in control group and experiment group. Normally the raw number of userids can't be used to compare the experiment results. Instead proportions should be used, like what's the proportion of users who enroll in the class given the number of users who click the 'start free trial' button.
+ *Number of clicks: That is, number of unique cookies to click the "Start free trial" button (which happens before the free trial screener is trigger).* This metric will also stay the same before and afer the invervention.
+ *Click­-through­-probability: That is, number of unique cookies to click the "Start free trial" button divided by number of unique cookies to view the course overview page.* This metric will also stay the same before and afer the invervention, because the change do not influence anything on the button itself. 
+ *Gross conversion: That is, number of user­ids to complete checkout and enroll in the free trial divided by number of unique cookies to click the "Start free trial" button.* This is one of the metrics that should be evaluated. If the users are really influenced by the 'number of hours' question, the proportion of enrollments will be increase or decrease.
+ *Retention: That is, number of user­ids to remain enrolled past the 14 ­day boundary (and thus make at least one payment) divided by number of user­ids to complete checkout.* This is another metric we want. If the question window really works, Udacity should expect more students remain enroll after the 14 day boundary because they are really able to finish the course.
+ *Net conversion: That is, number of user­ids to remain enrolled past the 14­day boundary (and thus make at least one payment) divided by the number of unique cookies to click the "Start free trial" button.* Likewise, this is the metric Udacity should evaluate.

Thus, I can state the invariant metrics and the evaluation metrics in our experiment.

##### Invariant Metrics:
+ Number of cookies: That is, number of unique cookies to view the course overview page. (dmin=3000) 
+ Number of clicks: That is, number of unique cookies to click the "Start free trial" button (which happens before the free trial screener is trigger). (dmin=240)
+ Click-through-probability: That is, number of unique cookies to click the "Start free trial" button divided by number of unique cookies to view the course overview page. (dmin=0.01)

##### Evaluation Metrics:
+ Gross conversion: That is, number of user­ids to complete checkout and enroll in the free trial divided by number of unique cookies to click the "Start free trial" button. (dmin=0.01)
+ Retention: That is, number of user­ids to remain enrolled past the 14 ­day boundary (and thus make at least one payment) divided by number of user­ids to complete checkout. (dmin=0.01)
+ Net conversion: That is, number of userids to remain enrolled past the 14-day boundary (and thus make at least one payment) divided by the number of unique cookies to click the "Start free trial" button. (dmin=0.0075)

After running of the testing, if the experiment group's gross conversion appears to be lower than the control group's and if the experiment group's retention and net conversion become higher then the control group's, I will definitely recommend to launch the modification.


#### Measuring Standard Deviation
+ I draw some statistics from the baseline data:
    + *define **PCONV** as "num of payments / unique cookies to click the btn", which is 0.1093125*
    + *define **CONV** as "num of enrollments / unique cookies to click the btn", which is 0.20625*
    + *define **ECONV** as "num of payments / number of enrollments", which is 0.53*
    + *click-through-rate, **CTR**: 0.08*

+ The quiz said the *Number of cookies to view the page, **V(n)**: 5000*
+ And thus the number of unique cookies to click the "Start free trail" button is N(c): 400
+ And thus the number of enrollments is N(e): 82.5

+ **Gross conversion**
    + $SE_g = \sqrt{CONV * (1 - CONV) / N(c)}$
    + 0.0202
    + The 

+ **Retention**
    + $SE_r = \sqrt{ECONV * (1 - ECONV) / N(e)}$
    + 0.0549

+ **Net Conversion**
    + $SE_n = \sqrt{PCONV * (1 - PCONV) / N(c)}$
    + 0.0156


#### Sizing

##### Number of Samples vs. Power
I will not use Bonferroni correction in my analysis phase.
Using [this calculator](http://www.evanmiller.org/ab-testing/sample-size.html), I calculated that: 
+ the total size for Gross Conversion will be: $25,835 * 2 / 0.08 = 645,875$
+ the total size for Retention will be: $39115 / 0.20625 * 2 / 0.08 = 4,741,212$
+ the total size for Net Conversion will be: $27,413 * 2 / 0.08 = 685,325$

Use alpha = 0.05 and beta = 0.2, the page views will be: Max(645,875, 4,741,212, 685,325) = 4,741,212

##### Duration vs. Exposure
Time matters. Udacity doesn't want to run this experiment for a long time. Suppose we want to finish the experiment within 1 month, that is 30 days. So The total traffic we need will be $40,000 * 30 = 1,200,000$. And the fraction should be $4,741,212\:/\:(40,000 * 30)\approx3.59$. This exceeds 1, which means Udacity can't open such a huge traffic. Back to choosing invariant metrics, I will give up measuring Retention under such a circumstance.

So the evalution metric I finally use will be:
+ **Gross conversion: That is, number of user­ids to complete checkout and enroll in the free trial divided by number of unique cookies to click the "Start free trial" button. (dmin=0.01)**
+ **Net conversion: That is, number of userids to remain enrolled past the 14-day boundary (and thus make at least one payment) divided by the number of unique cookies to click the "Start free trial" button. (dmin=0.0075)**

Use alpha = 0.05 and beta = 0.2, the final page views will be: Max(645,875, 685,325) = 685,325.

And the fraction should be: $685,325\:/\:(40,000 * 30)\approx0.57$

This experiment only ask Udacity's customer about how many hours they will spend on their classes each week. Basically this will not harm them. And the data itself is not a sensitive information. On the other hand, if Udacity see the number of payments suddenly become low after the experiment is launched, they can simply stop the testing phase. I can therefore conclude that it's a low risky experiment for Udacity.

### Experiment Analysis

#### Sanity Checks
The table below records the Sanity Checks I did for the data I get. The Lower Bound and Upper Bound shows the confidence interval for the value I expected. All of the three invariance metrics passed the Sanity Checks. So I can move on to next steps in the analysis process.

|                                               |Lower Bound|Upper Bound|Observed|Passes|
|---                                            |---        |---        |---     |---   |
|Number of Cookies                              |0.4988     |0.5012     |0.5006  |Y     |
|Number of Clicks on "Start Free Trial"         |0.4959     |0.5041     |0.5005  |Y     |
|Click-through-probability on "Start Free Trial"|-0.0013    |0.0013     |0.0001  |Y     |

#### Result Analysis

##### Effect Size Tests
The table below shows the confidence interval around the difference for each evaluation metrics.

|                 |Lower Bound|Upper Bound|Statistical significance|Practical significance|dmin    |
|---              |---        |---        |---                     |---                   |---     |
|Gross Conversion |-0.0291    |-0.01199   |Y                       |Y                     |0.01    |
|Net Conversion   |-0.0116    |0.00186    |N                       |N                     |0.0075  |

For Gross Conversion, the point estimate is smaller than the -dmin boundary, which means it's practical significance. The confidence interval lays outside the -dmin boundary, so it's also statistical significance.

For Net Conversion, the point estimate lays inside the [-dmin, dmin] boundary and the confidance interval contains 0, so it's neither practical significance nor statistical significance.

##### Sign Tests
The table below shows the sign tests result for each evaluation metrics.

|                 |p-value|Statistical significance|
|---              |---    |---                     |
|Gross Conversion |0.0026 |Y                       |
|Net Conversion   |0.6776 |N                       |

The gross conversion's p-value is less than the chosen $\alpha$ value, 0.05. So it's statistical significance. However, the net conversion's p-value means the result seems to come out by chance. It's not statistical significance.

##### Summary
I'm not using Bonferroni correction here for the following reasons.
+ The Bonferroni correction are mainly used to decrease the probability of Type I error.
+ Here ALL metrics should match the criteria in order to launch, which will be strongly impacted by a single false negative, or Type II error.
+ If Udacity use Bonferroni correction here, the result will be too conservative to let all metrics match the criteria. It's a waste of time and money.


#### Recommendation
Based on the gross conversion data, the number of students who enroll in the free trial definitely goes down after the change. However, the net conversion is not so clear. From the results of effect size tests, the net conversion doesn't have statistical significance, for the CI includes 0. It also doesn't have practical significance, because 0.0075 is included in the Confidence Interval. Udacity must do a more precise experiment to confirm on this point and draw a final decision about whether to launch.

### Follow-Up Experiment
I will run an A/B Test, where users in the experiment group will receive a quiz before formal enroll in the course (that is, complete checkout and start the 14 day free trial period). The quiz can reflect how much does the student know about the prior or related knowledge about this course. If the student can pass the quiz, then he or she can enroll in this course. On the other hand, a student who fails on quiz will get a warn that he or she are more likely to quit this class finally and it is recommended for them to use the free course material.

Here I can use the same invariant metrics as the Udacity A/B Testing:
+ Number of cookies: That is, number of unique cookies to view the course overview page.
+ Number of clicks: That is, number of unique cookies to click the "Start free trial" button (which happens before the free trial screener is trigger).
+ Click-through-probability: That is, number of unique cookies to click the "Start free trial" button divided by number of unique cookies to view the course overview page.

The unit diversion is a cookie, user-ids will be used once the student enroll in the free trial.

And I will use the following evalution metrics:
+ Gross conversion: That is, number of user­ids to complete checkout (and thus take the quiz) and enroll in the free trial divided by number of unique cookies to click the "Start free trial" button.
+ Post Quit Probability: That is, number of user­ids to quit the course past the 14 ­day boundary divided by number of user­ids to complete checkout.
+ Pre Quit Probability: That is, number of userids to quit the course within the 14 day boundary divided by number of unique cookies to click the "Start free trial" button.

The null hypothesis would be: Gross conversion, Post and Pre Quit Probability remains same after the testing.