# road_surface_classification
Description: This repo contains project materials for Driving for Science, a machine learning project that uses tri-axial smartphone accelerometer data to classify road surface conditions among three categories, potholes, normal roads, and speed bumps using a custom 1D CNN, for CSCI 0451 - Machine Learning, Spring 2026.

Group Member: Samuel Cramer

## Required Packages
folium
gpxpy

Abstract: 
This project addresses the problem of limited existing data describing the road surface damage by using three-axis smartphone accelerometer data to classify road surface conditions. We will use a 1D Convolutional Neural Network (CNN) implemented from scratch in PyTorch to classify road features into three classes: normal road, speed bump, and pothole. Data will be self-collected in the local vicinity of Middlebury College using an iPhone accelerometer and GPS, and the data will be labeled by synchronizing event logs (collected during data acquisition) with our accelerometer data to develop set time windows for training. The success of our project will be evaluated on precision, recall, and F1-score for each of our classes for each temporal window compared to a logistic regression baseline, with the ultimate goal of creating a road quality map in the town of Middlebury. 

Motivation and Question:
Monitoring roads for quality in Vermont is tedious when done manually, and road work struggles to keep pace with the damage caused by winter weather conditions. However, due to the near omnipresence of smartphones, we essentially have a network of mobile sensors already deployed in the field. As a Vermont driver, the potential to create a passive monitoring system using smartphone accelerometers is appealing, as being able to more easily identify and locate potholes with road data could translate to localities having an improved ability to allocate resources to repair roads. Using a self-collected dataset from a 3-axis accelerometer and GPS data from smartphones driven over roads around the town of Middlebury, we will investigate the question: Can a machine learning model be used to reliably classify road surfaces between smooth roads, speed bumps, and potholes? Achieving successful classification will provide better infrastructure data to the municipalities that maintain it.

Planned Deliverables:
Full Success:
	Python Package that includes a full data pipeline that combines CSV and GPS GPX data into a labeled dataset.
	1D CNN model that is trained to distinguish the three road classes we have defined/
	Jupyter Notebook that cleanly demonstrates the translation from the raw data we took on the road and the analytical steps we took afterward.
	Map that has three road surface types classified and overlaid over the Middlebury road network.
Partial Success:
	Completed data collection and pipeline.
	A PyTorch model that demonstrates some training and performance metrics for classifying the three road types.
	Analysis of accelerometer data in Jupyter notebook. 


Resources Requried:
Data: Training and validation data will be self-collected using two iPhones. One iPhone will record timestamped accelerometer data using the Physics Toolbox application, and the other will record timestamped GPS data using Open GPX Tracker. Labels will be provided through a custom Python script running on a laptop that has the passenger log timestamps to indicate pothole or speedbump events.
I didn't think that I needed to link a dataset for my case, but if required specifically for the proposal, I have found a link to a dataset I can use potentially for comparison that contains the feature of z-axis acceleration, as well as the targets in labeled data. Link: https://www.accelerometer.xyz/datasets/
Source: [Gonzalez 2017] Learning Roadway Surface Disruption Patterns Using the Bag of Words Representation


Computer: Standard Apple Silicon Laptop
Software: Python, PyTorch, pandas(data wrangling and visualization), gpxpy(gps wrangling), folium (map integration).

What I Will Learn:
I will learn how to use real-world data, build labels, and create a 1D CNN model from scratch that works with temporal parameters. I'll also have time to explore how to keep discipline on a solo software project, learn how to integrate data with maps, and perform complex data wrangling, recognizing the imperfection that hardware contexts can provide.

Risk Statement:
I think one risk is that I may not be able to create enough labeled data, as there might just not be enough speed bumps or potholes in the Middlebury area. I could get around this however by exploring other areas in Addison County to get more labeled data.

Another risk is that creating labels may have some latency due to human error. However, this could be fixed by having our training time windows shift up accordingly to account for this disconnect between a real event and a record.

Ethics Statement: 
1. The overall impact on the world would be relatively positive, as being able to monitor potholes and assign geographic locations to them would provide attention to infrastructure networks that need help, ameliorating conditions for communities, governments, and drivers alike.
2. Communities may benefit from this project, as their infrastructure may receive targeted funding to help them improve their roads. Drivers may benefit from this project, as they may have a more pleasurable driving experience if road surfaces are identified for fixing, and they also may spend less money replacing car suspensions if roads are of better quality. Finally, governments may benefit from this project, as surveying roads may be costly and passive monitoring may more efficiently identify infrastructure faults.
3. A group that may be harmed or excluded from the project could be drivers, as if their data is misused, it may be used to track them and pass on some sort of advertisement or increased costs in some malicious way if sold to a third-party. Furthermore, road surfaces that are poor but aren't detected by the model may lead to a certain area being neglected from road funds and road improvement.
4. I believe that the world will become an overall better place because of this project, as it will provide easy identification of road surfaces that need to be improved, without necessitating expensive manual monitoring work. One assumption behind this answer include that the governments and municipalities will use the data generated by this project to strategically put work and funds towards the improvement of the identified poor road segment. Another is that repairs will be completed based on the severity of the damage, rather than the frequency of travel over a damaged area.

Tentative Timeline:
End of week 9: Data Collected from 20km of driving & data pipelines created. 
Week 10 (2 week check-in): Notebook containing some signal traits for each of the three classes
Week 11: Model development, fine tuning, and integration with folium. 
Week 12: Completely 1D CNN model compared against simpler models, Jupyter notebook, and final report completed, presentation ready. 
