import * as React from 'react'
import { FaTwitter, FaGithub, FaLinkedin } from 'react-icons/fa'
import { IoSunnyOutline, IoMoonSharp } from 'react-icons/io5'
import * as config from 'lib/config'

import styles from './styles.module.css'

// TODO: merge the data and icons from PageSocial with the social links in Footer

export const Footer: React.FC<{
  isDarkMode: boolean
  toggleDarkMode: () => void
}> = ({ isDarkMode, toggleDarkMode }) => {
  const toggleDarkModeCb = React.useCallback(
    (e) => {
      e.preventDefault()
      toggleDarkMode()
    },
    [toggleDarkMode]
  )

  return (
    <footer className={styles.footer}>
      <div className={styles.copyright}><a href="https://github.com/underhood-club">GitHub</a></div>

      <div className={styles.social}>
        <a
                  className={styles.toggleDarkMode}
                  onClick={toggleDarkModeCb}
                  title='Tottle dark mode'
                >
                  {isDarkMode ? <IoMoonSharp /> : <IoSunnyOutline />}
                </a>
      </div>
    </footer>
  )
}
