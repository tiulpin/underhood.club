import fixer from "./migrator";

fixer('tweets', 'dump-old', 'dump-old',
  content => content
)
