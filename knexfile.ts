import type { Knex } from "knex";

// Update with your config settings.

const config: { [key: string]: Knex.Config } = {
  development: {
    client: "pg",
    connection: {
      host: 'ec2-52-207-90-231.compute-1.amazonaws.com',
      port: 5432,
      user: '',
      password: '',
      database: 'dcps4e32kl8qkb',
      ssl: {
        rejectUnauthorized: false
      },
    },
    migrations: {
      directory: 'server/migrations',
      tableName: 'knex_migrations'
    },
    seeds: {
      directory: 'server/seeds'
    },
  },

};

export default config;
