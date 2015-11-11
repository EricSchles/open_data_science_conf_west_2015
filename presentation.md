#Building Systems to Fight Slavery

__By__

__Eric__ __Schles__

##About Me

* Worked for Manhattan District Attorney's Human Trafficking Response Unit as Data Science Researcher
* Currently work for the United States Digital Service as a Data Scientist working on Veterans Affairs
* Still working as a researcher in Human Trafficking in my spare time 

##Problem Definition

Human Trafficking <=> Slavery

Today we'll be focusing on Sex Trafficking.

Sex trafficking happens a few ways:

1. A person is kidnapped and forced into sex slavery 
2. A person is mentally/physcially violated to such an extreme place, they submit to the will of the trafficker

A possible solution to 1 - Match missing persons pictures with pictures from sex marketplace websites such as backpage

Solving 2 is harder.  To understand how to stop problem 2, we must understand the approach a trafficker uses to break his victims:

1. The trafficker cuts off the victims social connections and emotional support center, refocusing this system souly on them ~ 3-7 months

2. Once the victim has no other or a very small social/emotional support center, the trafficker begins to physically beat the victim or rape them ~ once per month

3. Then the victim is moved into a small living quarters with other victims and made to compete for the traffickers attention and affection by making the trafficker money.  

4. The trafficker reinforces a pattern of control with a combination of violence, rape, and occasionally consential sex. ~ beats or rapes them once per month.  Trafficker says the victim will be beat or raped nearly constantly.  At this point the victim is trapped. 

Presently law enforcement attacks the problem by intervening when the victim is in stage 4.  Sometimes we are able to intervene sooner, but usually we are not.  

What we need is a system that understands the __contributing__ __factors__ that led to that person becoming a victim in the first place and understand the "basket" of policy choices they can employ to limit the amount of trafficking and to hit reasonable goals to reduce human trafficking supply.

The system I am building addresses this question - how do we build analyses that will aid the in combatting human trafficking, not just when a person has become a victim, but how do we stop them from becoming a victim?

##The system

In the current state the system performs automated investigations into human trafficking.  

So how does law enforcement decide what might be human trafficking?

Primarily it looks at cases involving violence and prostitution.  

[Demo of Web Scraper goes here]()

Web Scraping an ad -> Running an investigation

The Address parse in action:

```
>>> from tools import *
>>> parse_addr = ParseAddress()
>>> #Get Lat/Long from an exact address
>>> parse_addr.parse("9 Poplar Court, Great Neck, NY, 11024")
Location((40.8088205083, -73.7369217892, 0.0))
>>> #Get Lat/Long from an exact address in free text
>>> parse_addr.parse("Hello there my name is Eric and I live at 9 Poplar Court, Great Neck, NY, 11024")
Location((40.8088205083, -73.7369217892, 0.0))
>>> #Get a Lat/Long from Cross Streets
>>> parse_addr.parse("Hello there my name is Eric and I live at Middle Neck and Steam Boat, Great Neck, NY, 11024")
Location((40.8006567, -73.7284647, 0.0))
```

My goal for this system is to get it into every police department in the country, so they can automatically run human trafficking investigations and gather evidence as fast as possible.  And so that they can come up with leads for future cases, by comparing against current cases.

My second goal is to get this system to send me anonymous data, detailing how many human trafficking investigations are run and sending that number to a central server.  With the frequency of cases being processed, we can get a sense for the number of human trafficking cases in an area.  

This data set, combined with:
* Education Data:
	* years of schooling in a given area
	* grade point average from grade to grade in a given area
	* percentage of people with GED/high school diploma in a given area
	* percentage of people with college degree in a given area
	* percentage of people with a masters or other graduate degree in a given area
	* more goes here
* Homelessness Data:
	* number of homeless families
	* number of homeless single men
	* number of homeless single women
	* number of homeless male children
	* number of homeless female children
	* number of homeless families with one parent
	* total number of homeless people
* Legal Data:
	* Number of Human Trafficking laws currently in affect in an area
	* Number of Human Trafficking bills that are being considered for becoming law
* Housing Data:
	* Number of Housing Developments in an area
	* Number of Apt. Buildings in an area
	* Number of building violations in total in an area
* Social Welfare Data
	* Unclear what's out there
* Crime Data:
	* Unclear how to get this everywhere

In total will give us a sense of the possible contributing factors to human trafficking.  From there we will be able to do analysis of the most important contributing factors, by region, using something called impulse response.

To understand impulse response we must first review time series analysis, in particular Vector Autoregression Models (VAR for short).

If you don't know or don't remember time series analysis, please check out [this great introduction on MA and AR models](http://www.analyticsvidhya.com/blog/2015/03/introduction-auto-regression-moving-average-time-series/).

[Timeseries Demo]()

Check out: [statsmodels docs](http://statsmodels.sourceforge.net/devel/vector_ar.html) for more info

If you want to help you can:

[http://hackingagainstslavery.github.io](http://hackingagainstslavery.github.io)
