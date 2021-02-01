import fixer from "./migrator";
import { merge } from "ramda";

fixer('info', 'dump-old', 'dump-old',
  (content) =>
    merge(
      content
    )
)
