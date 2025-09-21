
--  Figure how to handle green score
CREATE TABLE journeys (
    id SERIAL PRIMARY KEY,
    origin_id VARCHAR(255) NOT NULL,
    origin_address VARCHAR(255) NOT NULL,
    destination_id VARCHAR(255) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    distance INT NOT NULL,
    transport_id BIGINT REFERENCES transports(id),
    green_score NUMERIC(5,2) NOT NULL, 
    num_passengers INT
);

-- CREATE TABLE journeys (
--     id SERIAL PRIMARY KEY,
--     origin_id VARCHAR(255) NOT NULL,
--     origin_address VARCHAR(255) NOT NULL,
--     destination_id VARCHAR(255) NOT NULL,
--     destination_address VARCHAR(255) NOT NULL,
--     distance INT NOT NULL,
--     type transport_type NOT NULL,
--     green_score NUMERIC(5,2) NOT NULL, 
--     emission_type emission_type,
--     engine_size NUMERIC(3, 1),
--     num_passengers INT
-- );

CREATE TYPE transport_type AS ENUM ('CAR', 'COACH', 'TRAIN');
CREATE TYPE emission_type AS ENUM ('ELECTRIC', 'HYBRID', 'DIESEL', 'PETROL');

-- Should exten to this but not used as of now
CREATE TABLE transports (
    id SERIAL PRIMARY KEY,
    nickaname VARCHAR(64) NOT NULL,
    type transport_type NOT NULL,
    engine_size NUMERIC(3, 1),
    emission_type emission_type,
    CONSTRAINT c_car_journey CHECK(transport_type != 'CAR' OR (engine_size IS NOT NULL AND emission_type IS NOT NULL))
);

CREATE TABLE users_journeys (
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    journey_id BIGINT NOT NULL REFERENCES journeys(id),
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    fixture_id BIGINT NOT NULL REFERENCES fixtures(id),
    PRIMARY KEY (user_id, fixture_id)
);

CREATE TABLE users_transports (
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    transport_id BIGINT NOT NULL REFERENCES transports(id),
    CONSTRAINT c_users_transports UNIQUE (user_id, transport_id)
);


CREATE TABLE clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE fixtures (
    home_club_id BIGINT NOT NULL REFERENCES clubs(id),
    away_club_id BIGINT NOT NULL REFERENCES clubs(id),
    start_time TIMESTAMP NOT NULL,
    id SERIAL PRIMARY KEY,
    CONSTRAINT c_fixtures_unique UNIQUE (home_club_id, away_club_id),
    CONSTRAINT c_fixtures_two_teams CHECK (home_club_id != away_club_id)
);

CREATE TABLE users (
    id VARCHAR(64) NOT NULL PRIMARY KEY,
    fname VARCHAR(64) NOT NULL,
    lname VARCHAR(64) NOT NULL,
    date_of_birth DATE NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE users_clubs (
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    CONSTRAINT c_user_clubs UNIQUE (user_id)
);


-- CREATE TABLE transport (
--     id SERIAL PRIMARY KEY,
--     type VARCHAR(32) NOT NULL,
--     engine_type VARCHAR(16),
--     engine_size NUMERIC(3, 1)
-- );

-- CREATE TABLE users_transport (
--     user_id BIGINT NOT NULL REFERENCES users(id),
--     transport_id BIGINT NOT NULL REFERENCES transport(reg),
--     PRIMARY KEY (user_id, car_reg) 
-- );


CREATE OR REPLACE FUNCTION delete_user(
    _user_id TEXT
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete from users_clubs
    DELETE FROM users_clubs
    WHERE user_id = _user_id;       
    -- Delete from users_journeys
    DELETE FROM users_journeys
    WHERE user_id = _user_id;
    -- Delete from users
    DELETE FROM users
    WHERE id = _user_id;
END;
$$;



CREATE OR REPLACE FUNCTION insert_journey(
    _fixture_id INT,
    _origin_id TEXT,
    _origin_address TEXT,
    _destination_id TEXT,
    _destination_address TEXT,
    _distance INT,
    _type transport_type,         -- enum, can be NULL
    _green_score NUMERIC, 
    _emission_type emission_type, -- enum, can be NULL
    _engine_size NUMERIC, -- can be NULL
    _num_passengers INT,
    _user_id TEXT,
    _club_id INT
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    new_journey_id INT;
BEGIN
    -- Insert into journeys
    INSERT INTO journeys (
        origin_id, origin_address, destination_id, destination_address, distance, type, green_score, emission_type, engine_size, num_passengers
    )
    VALUES (
        _origin_id,
        _origin_address,
        _destination_id,
        _destination_address,
        _distance,
        _type,               -- can be NULL
        _green_score,
        _emission_type,      -- can be NULL
        _engine_size,
        _num_passengers
    )
    RETURNING id INTO new_journey_id;

    -- Insert into users_journeys
    INSERT INTO users_journeys (
        user_id, journey_id, club_id, fixture_id
    )
    VALUES (
        _user_id, new_journey_id, _club_id, _fixture_id
    );
END;
$$;


CREATE OR REPLACE FUNCTION delete_journey_for_user(
    _journey_id INT,
    _user_id TEXT
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete from users_journeys
    DELETE FROM users_journeys
    WHERE journey_id = _journey_id AND user_id = _user_id;

    -- Delete from journeys if no other references exist
    IF NOT EXISTS (
        SELECT 1 FROM users_journeys WHERE journey_id = _journey_id
    ) THEN
        DELETE FROM journeys WHERE id = _journey_id;
    END IF;
END;
$$;