import { underhood, curator } from '../underhood'

export default function (str) {
  return str
    .replace(/{{underhood.name}}/g, underhood.name)
    .replace(/{{underhood.description}}/g, underhood.description)
    .replace(/{{curator.twitter}}/g, curator.twitter)
}
