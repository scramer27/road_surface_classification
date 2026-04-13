# road_surface_classification
Description: This repo contains project materials for Driving for Science, a machine learning project that uses tri-axial smartphone accelerometer data to classify road surface conditions among three categories, potholes, normal roads, and speed bumps using a custom 1D CNN, for CSCI 0451 - Machine Learning, Spring 2026.

Group Member: Samuel Cramer

Abstract: 
This project addresses the problem of limited existing data describing the road surface damage by using three-axis smartphone accelerometer data to classify road surface conditions. We will use a 1D Convolutional Neural Network (CNN) implemented from scratch in PyTorch to classify road features into three classes: normal road, speed bump, and pothole. Data will be self-collected in the local vicinity of Middlebury College using an iPhone accelerometer and GPS, and the data will be labeled by synchronizing event logs (collected during data acquisition) with our accelerometer data to develop set time windows for training. The success of our project will be evaluated on precision, recall, and F1-score for each of our classes for each temporal window compared to a logistic regression baseline, with the ultimate goal of creating a road quality map in the town of Middlebury. 

Motivation and Question:
Monitoring roads for quality in Vermont is tedious when done manually, and road work struggles to keep pace with the damage caused by winter weather conditions. However, due to the near omnipresence of smartphones, we essentially have a network of mobile sensors already deployed in the field. As a Vermont driver, the potential to create a passive monitoring system using smartphone accelerometers is appealing, as being able to more easily identify and locate potholes with road data could translate to localities having an improved ability to allocate resources to repair roads. Using a self-collected dataset from a 3-axis accelerometer and GPS data from smartphones driven over roads around the town of Middlebury, we will investigate the question: Can a machine learning model be used to reliably classify road surfaces between smooth roads, speed bumps, and potholes? Achieving successful classification will provide better infrastructure data to the municipalities that maintain it.

Planned Deliverables:

Resources Requried:

What I Will Learn:

Risk Statement:

Ethics Statement:

Tentative Timeline:
