use studentjournaldb;

SET FOREIGN_KEY_CHECKS=0;
DELETE FROM `studentjournaldb`.`users_appuser`
WHERE username != "admin";

SET FOREIGN_KEY_CHECKS=1;
