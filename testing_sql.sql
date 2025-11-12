-- Reset
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;

-- testing insertions
/*
Severs:
1: 1326491726319452222
2: 679668079005007872
Channels:
1a: 1326491790613938219
2a: 1261711896281874432

*/
INSERT INTO servers VALUES (1326491726319452222), (679668079005007872);
INSERT INTO rps (name, description, universe_name, is_enabled, curr_time_rp, 
    tickinterval_rp, tickinterval_real, update_channel_id) VALUES
    ('One', '', '', TRUE, '1980-01-01 00:00:00', '1 month', '1 hour', 1326491790613938219),
    ('Two', '', '', TRUE, '1920-01-01 00:00:00', '1 month', '10 minutes', 1261711896281874432);

INSERT INTO server_rp_table VALUES (1326491726319452222, 1), (1326491726319452222, 2), (679668079005007872, 2);

-- events
INSERT INTO tick_events (execution_time, status, rp_id) VALUES
    ('1920-11-12 23:00:00', 'completed', 1),
    ('2025-11-12 23:00:00', 'pending', 1),
    ('2025-11-12 23:30:00', 'pending', 2);
