DO $$
BEGIN
    EXECUTE format('ALTER DATABASE %I SET timezone TO %L', current_database(), 'America/Sao_Paulo');
END
$$;

-- Tables
CREATE TABLE IF NOT EXISTS clients (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	cpf VARCHAR(11) NOT NULL, 
	monthly_income NUMERIC(12, 2) NOT NULL, 
	usual_city VARCHAR(80) NOT NULL, 
	usual_start_time TIME WITHOUT TIME ZONE NOT NULL, 
	usual_end_time TIME WITHOUT TIME ZONE NOT NULL, 
	active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (cpf)
);

CREATE TABLE IF NOT EXISTS rules (
	id SERIAL NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	weight INTEGER NOT NULL, 
	threshold NUMERIC(12, 2), 
	window_minutes INTEGER, 
	active BOOLEAN DEFAULT true NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_rules_weight_range CHECK (weight BETWEEN 1 AND 100), 
	CONSTRAINT ck_rules_threshold_non_negative CHECK (threshold IS NULL OR threshold >= 0), 
	CONSTRAINT ck_rules_window_positive CHECK (window_minutes IS NULL OR window_minutes > 0), 
	UNIQUE (code)
);

CREATE TABLE IF NOT EXISTS transactions (
	id SERIAL NOT NULL, 
	client_id INTEGER NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	transaction_type VARCHAR(30) NOT NULL, 
	destination VARCHAR(100) NOT NULL, 
	location VARCHAR(80) NOT NULL, 
	occurred_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	risk_score INTEGER DEFAULT '0' NOT NULL, 
	classification VARCHAR(20) DEFAULT 'NORMAL' NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_transactions_amount_positive CHECK (amount > 0), 
	CONSTRAINT ck_transactions_risk_score_range CHECK (risk_score BETWEEN 0 AND 100), 
	CONSTRAINT ck_transactions_classification CHECK (classification IN ('NORMAL', 'ATTENTION', 'SUSPICIOUS')), 
	FOREIGN KEY(client_id) REFERENCES clients (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS alerts (
	id SERIAL NOT NULL, 
	transaction_id INTEGER NOT NULL, 
	rule_id INTEGER NOT NULL, 
	reason TEXT NOT NULL, 
	points INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_alerts_transaction_rule UNIQUE (transaction_id, rule_id), 
	CONSTRAINT ck_alerts_points_positive CHECK (points > 0), 
	CONSTRAINT ck_alerts_reason_not_blank CHECK (reason !~ '^\s*$'), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id) ON DELETE CASCADE, 
	FOREIGN KEY(rule_id) REFERENCES rules (id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_alerts_rule_id ON alerts (rule_id);
CREATE INDEX IF NOT EXISTS ix_alerts_transaction_id ON alerts (transaction_id);
CREATE INDEX IF NOT EXISTS ix_transactions_client_id ON transactions (client_id);
CREATE INDEX IF NOT EXISTS ix_transactions_occurred_at ON transactions (occurred_at);

INSERT INTO rules (code, name, description, weight, threshold, window_minutes) VALUES
    ('ATYPICAL_VALUE', 'Atypical amount', 'Amount above the client''s average over the last window_minutes plus threshold standard deviations (window: 30 days).', 30, 3, 43200),
    ('HIGH_FREQUENCY', 'High frequency', 'At least threshold transactions by the same client within window_minutes.', 25, 5, 10),
    ('UNUSUAL_HOUR', 'Unusual hour', 'Transaction outside the client''s usual hours, with a tolerance of threshold minutes (0 = strict).', 15, 0, NULL),
    ('REPEATED_SIMILAR', 'Repeated similar transactions', 'At least threshold transactions with the same amount and destination within window_minutes.', 25, 3, 60),
    ('CONSECUTIVE_INCREASING', 'Consecutive increasing amounts', 'Sequence of threshold transactions, each larger than the previous one, within window_minutes.', 20, 3, 60),
    ('PROFILE_MISMATCH', 'Incompatible with client profile', 'Amount greater than threshold times the client''s declared monthly income (0.50 = 50%).', 20, 0.50, NULL),
    ('UNUSUAL_LOCATION', 'Unusual location', 'Transaction location differs from the client''s usual city.', 20, NULL, NULL)
ON CONFLICT (code) DO NOTHING;