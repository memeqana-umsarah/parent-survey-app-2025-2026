CREATE DATABASE IF NOT EXISTS parent_survey
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE parent_survey;

DROP TABLE IF EXISTS survey_answers;
DROP TABLE IF EXISTS survey_responses;
DROP TABLE IF EXISTS school_totals;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    student_name VARCHAR(255) NOT NULL,
    grade VARCHAR(50),
    school VARCHAR(255),
    survey_type VARCHAR(20) DEFAULT 'E1'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE school_totals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school VARCHAR(255) NOT NULL UNIQUE,
    total_students INT NOT NULL DEFAULT 0
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE survey_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    student_name VARCHAR(255),
    grade VARCHAR(50),
    school VARCHAR(255),
    survey_type VARCHAR(20),
    respondent_type VARCHAR(100),
    other_respondent_text VARCHAR(255),
    bus_subscribed VARCHAR(10),
    bus_number VARCHAR(100),
    notes TEXT,
    overall_avg DECIMAL(5,2),
    overall_pct DECIMAL(5,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_school (school),
    INDEX idx_survey_type (survey_type)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE survey_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    response_id INT NOT NULL,
    survey_type VARCHAR(20),
    axis VARCHAR(255),
    question_id INT,
    question_text TEXT,
    answer_text VARCHAR(100),
    answer_value INT,
    CONSTRAINT fk_survey_answers_response
        FOREIGN KEY (response_id)
        REFERENCES survey_responses(id)
        ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
