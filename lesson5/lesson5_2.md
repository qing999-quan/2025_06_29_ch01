### 創建公司資料庫

```sql
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS  branch CASCADE;
DROP TABLE IF EXISTS client  CASCADE;
DROP TABLE IF EXISTS works_with CASCADE;
```

#### 創立員工表格

```
CREATE TABLE employee(
	emp_id SERIAL,
	name VARCHAR(20),
	birth_date DATE,
	sex VARCHAR(1),
	salary INT,
	branch_id INT,
	sup_id INT,
 	PRIMARY KEY(emp_id)
);
```

> [參考語法foreign key](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-foreign-key*/)

