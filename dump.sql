-- CREATE TABLE users (
-- 	id INTEGER NOT NULL, 
-- 	username VARCHAR(100) NOT NULL, 
-- 	email VARCHAR(100) NOT NULL, 
-- 	hashed_password VARCHAR, 
-- 	is_active BOOLEAN, role VARCHAR(100), 
-- 	PRIMARY KEY (id), 
-- 	UNIQUE (email), 
-- 	UNIQUE (username)
-- );
-- INSERT INTO users VALUES(4,'khashayar','khashayar@email.com','$2b$12$MkrqzpseRzNJZdxo7NaFpeG4MF/aKCx23wWV4kVf8cNereSUlPQiW',true,'admin');
INSERT INTO users VALUES(5,'jafar','jafar@email.com','$2b$12$MkrqzpseRzNJZdxo7NaFpeG4MF/aKCx23wWV4kVf8cNereSUlPQiW',true,'admin');
-- CREATE TABLE books (
-- 	id INTEGER NOT NULL, 
-- 	title VARCHAR NOT NULL, 
-- 	author VARCHAR NOT NULL, 
-- 	summary VARCHAR, 
-- 	category VARCHAR, 
-- 	owner_id INTEGER, 
-- 	PRIMARY KEY (id), 
-- 	FOREIGN KEY(owner_id) REFERENCES users (id)
-- );
INSERT INTO books VALUES(2,'Atomic Habits','James Clear','''Atomic Habits'' by James Clear explores the power of small habits and their cumulative effect on achieving significant change. Clear emphasizes the importance of focusing on systems rather than goals, providing actionable strategies to build good habits and break bad ones. The book encourages readers to make tiny, incremental changes to improve their daily lives over time.','Self-help',4);
INSERT INTO books VALUES(3,'Deep Work','Cal Newport','"Deep Work" by Cal Newport emphasizes the importance of focused, distraction-free work in achieving high productivity and honing skills. Newport contrasts deep work with shallow work, encouraging readers to cultivate the former through disciplined routines and environments. He offers practical strategies for minimizing distractions, setting aside time for deep focus, and ultimately reaching greater professional success and personal satisfaction.','Productivity',5);
INSERT INTO books VALUES(4,'Designing Data-Intensive Applications','Martin Kleppmann','"Designing Data-Intensive Applications" by Martin Kleppmann explores the architecture and design principles necessary for building robust, scalable, and maintainable data systems. It covers various models of data storage, handling schema evolution, and the intricacies of distributed systems. The book emphasizes trade-offs between consistency, availability, and partition tolerance, providing practical guidance on how to tailor solutions to specific applications. Additionally, it offers insights into tools and technologies in modern data processing.','Non-fiction',5);
-- CREATE INDEX ix_users_id ON users (id);
-- CREATE INDEX ix_books_id ON books (id);
