-- MySQL dump 10.14  Distrib 5.5.33-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: internote
-- ------------------------------------------------------
-- Server version	5.5.33-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `academic_year`
--

DROP TABLE IF EXISTS `academic_year`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `academic_year` (
  `academic_year_id` int(11) NOT NULL AUTO_INCREMENT,
  `academic_year_name` varchar(30) DEFAULT NULL,
  `academic_year_divided_in` varchar(11) DEFAULT NULL,
  `academic_year_created_at` datetime DEFAULT NULL,
  `academic_year_updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`academic_year_id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `academic_year`
--

LOCK TABLES `academic_year` WRITE;
/*!40000 ALTER TABLE `academic_year` DISABLE KEYS */;
/*!40000 ALTER TABLE `academic_year` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account` (
  `account_id` int(11) NOT NULL AUTO_INCREMENT,
  `account_company_name` text,
  `account_username` text,
  `account_password` text,
  `account_email` text,
  `account_code_number` varchar(10) DEFAULT NULL,
  `account_code_number_date` datetime DEFAULT NULL,
  `account_school_localization` text,
  `account_postal_address` text,
  `account_phone1` varchar(15) DEFAULT NULL,
  `account_phone2` varchar(15) DEFAULT NULL,
  `account_print_header_image_name` text,
  `account_print_header_minister` varchar(250) DEFAULT NULL,
  `account_created_at` datetime DEFAULT NULL,
  `account_updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `class` (
  `class_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_name` varchar(50) DEFAULT NULL,
  `class_created_at` datetime DEFAULT NULL,
  `class_updated_at` datetime DEFAULT NULL,
  `academic_year_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`class_id`)
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classroom`
--

DROP TABLE IF EXISTS `classroom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classroom` (
  `classroom_id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_name` varchar(50) DEFAULT NULL,
  `classroom_created_at` datetime DEFAULT NULL,
  `classroom_updated_at` datetime DEFAULT NULL,
  `class_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`classroom_id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classroom`
--

LOCK TABLES `classroom` WRITE;
/*!40000 ALTER TABLE `classroom` DISABLE KEYS */;
/*!40000 ALTER TABLE `classroom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mark`
--

DROP TABLE IF EXISTS `mark`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mark` (
  `mark_id` int(11) NOT NULL AUTO_INCREMENT,
  `mark_mark` double DEFAULT NULL,
  `mark_level` int(11) DEFAULT NULL,
  `mark_observation` text,
  `mark_date` varchar(100) DEFAULT NULL,
  `mark_group` varchar(50) DEFAULT NULL,
  `student_id` int(11) DEFAULT NULL,
  `topic_id` int(11) DEFAULT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  `academic_year_id` int(11) DEFAULT NULL,
  `mark_created_at` datetime DEFAULT NULL,
  `mark_updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`mark_id`)
) ENGINE=InnoDB AUTO_INCREMENT=287 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mark`
--

LOCK TABLES `mark` WRITE;
/*!40000 ALTER TABLE `mark` DISABLE KEYS */;
/*!40000 ALTER TABLE `mark` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student` (
  `student_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_first_name` varchar(50) DEFAULT NULL,
  `student_last_name` varchar(100) DEFAULT NULL,
  `student_birth_date` varchar(50) DEFAULT NULL,
  `student_birth_place` varchar(100) DEFAULT NULL,
  `student_genre` varchar(10) DEFAULT NULL,
  `student_height` int(11) DEFAULT NULL,
  `student_matricule` varchar(200) DEFAULT NULL,
  `student_matricule_ministeriel` varchar(200) DEFAULT NULL,
  `student_previous_school` varchar(200) DEFAULT NULL,
  `student_previous_classroom` varchar(50) DEFAULT NULL,
  `student_statut` varchar(20) DEFAULT NULL,
  `student_redoubler` varchar(5) DEFAULT NULL,
  `student_email` varchar(255) DEFAULT NULL,
  `student_phone1` varchar(15) DEFAULT NULL,
  `student_phone2` varchar(15) DEFAULT NULL,
  `student_phone3` varchar(15) DEFAULT NULL,
  `student_photo_name` text,
  `student_created_at` datetime DEFAULT NULL,
  `student_updated_at` datetime DEFAULT NULL,
  `academic_year_id` int(11) DEFAULT NULL,
  `class_id` int(11) DEFAULT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=190 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `topic`
--

DROP TABLE IF EXISTS `topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `topic` (
  `topic_id` int(11) NOT NULL AUTO_INCREMENT,
  `topic_name` varchar(100) DEFAULT NULL,
  `topic_coef` int(11) DEFAULT NULL,
  `topic_type` varchar(100) DEFAULT NULL,
  `topic_prof` varchar(255) DEFAULT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  `topic_created_at` datetime DEFAULT NULL,
  `topic_updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`topic_id`)
) ENGINE=InnoDB AUTO_INCREMENT=487 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `topic`
--

LOCK TABLES `topic` WRITE;
/*!40000 ALTER TABLE `topic` DISABLE KEYS */;
/*!40000 ALTER TABLE `topic` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-08-17 20:15:04
