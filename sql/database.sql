-- Keep the user link (this is safe and good practice)
ALTER TABLE completed_tasks
ADD CONSTRAINT fk_completed_user 
FOREIGN KEY (userid) REFERENCES users(userid);

-- DO NOT add the taskid foreign key. 
-- If you already added it, drop it now:
ALTER TABLE completed_tasks 
DROP CONSTRAINT completed_tasks_taskid_fkey;