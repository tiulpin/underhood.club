import migrateInfo from './migrator/migrate-info'
import migrateFollowers from './migrator/migrate-followers'
import migrateTweets from './migrator/migrate-tweets'

migrateInfo()
migrateFollowers()
migrateTweets()
