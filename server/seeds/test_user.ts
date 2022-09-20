import { Knex } from "knex";

export async function seed(knex: Knex): Promise<void> {
    const [ { id: userId } ] = await knex('user').insert({
        email: 'upallnate@gmail.com',
        name: 'Up All Nate'
    }).onConflict('email').merge().returning('id')

    const [ { id: licenseId } ] = await knex('license').insert({
        userId
    }).returning('id')

    console.log({ licenseId })
};
