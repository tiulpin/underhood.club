import { ensureFileSync, ensureDirSync } from 'fs-extra';
import areas from './areas';

export default function ensureAuthorFiles(username) {
    ensureDirSync('./dump/images');
    areas.map(area => {
        ensureFileSync(`./dump/${username}-${area}.json`);
    });
}
