export const validateEnv = () => {
  const {PORT, SECRET, MAYO, CURRYSAUCE} = process.env
  if (!PORT || !SECRET || !MAYO || !CURRYSAUCE) {
    throw Error('Please provide the required variables')
  }

  const {HTTPS, CRT, PK} = process.env
  if (HTTPS && HTTPS === 'true' && !CRT && !PK) {
    throw Error('Provide the certificates information to start server')
  }

  const {EXPPATH} = process.env
  if (!EXPPATH) {
    console.log('experimenter folder not defined, using default')
  }
}
