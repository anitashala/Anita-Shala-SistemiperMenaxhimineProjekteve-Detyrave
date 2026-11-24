-- Skema e databazës (MySQL 8, InnoDB). Ekzekutoje një herë:
--   mysql -u root -p < migrations/schema.sql

CREATE DATABASE IF NOT EXISTS task_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE task_manager;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'USER',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_users_role CHECK (role IN ('USER', 'ADMIN'))
);

CREATE TABLE projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  deadline DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE project_members (
  project_id INT NOT NULL,
  user_id INT NOT NULL,
  member_role VARCHAR(20) NOT NULL DEFAULT 'MEMBER',
  joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (project_id, user_id),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT chk_member_role CHECK (member_role IN ('OWNER', 'MEMBER'))
);

CREATE TABLE tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,
  assigned_to INT NULL,
  created_by INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  description TEXT,
  status VARCHAR(20) NOT NULL DEFAULT 'TODO',
  priority VARCHAR(10) NOT NULL DEFAULT 'MEDIUM',
  deadline DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id),
  CONSTRAINT chk_task_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE')),
  CONSTRAINT chk_task_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH'))
);

CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  task_id INT NOT NULL,
  author_id INT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES users(id),
  CONSTRAINT chk_comment_content CHECK (CHAR_LENGTH(TRIM(content)) > 0)
);

CREATE INDEX idx_tasks_deadline ON tasks(deadline);
