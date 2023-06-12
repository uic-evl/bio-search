export const validateEnv = () => {
  const {PORT, SECRET, MAYO, CURRYSOUP} = process.env
  if (!PORT || !SECRET || !MAYO || !CURRYSOUP) {
    throw Error('Please provide the required variables')
  }

  const {HTTPS, CRT, PK} = process.env
  if (HTTPS && HTTPS === 'true' && !CRT && !PK) {
    throw Error('Provide the certificates information to start server')
  }
}
