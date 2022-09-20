import { Knex } from "knex";


export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('user', table => {
    table.increments('id').primary()
    table.string('name')
    table.string('email').notNullable().unique()
  }).createTable('license', table => {
    table.uuid('id').primary().notNullable().defaultTo(knex.raw('gen_random_uuid()'))
    table.integer('userId').references('user.id').notNullable()
  })
}


export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTable('license')
  .dropTable('user')
}

