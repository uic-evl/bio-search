import {Request, Response, NextFunction} from 'express'
import {appendFileSync} from 'fs'

export const logResult = (req: Request, res: Response, next: NextFunction) => {
  const {uid, condition, docId, decision, completionTime} = req.body
  const filename = `${uid}.csv`
  const timestamp = Date.now()

  const row = `${uid},${condition},${docId},${decision},${completionTime},${timestamp}\n`
  appendFileSync(filename, row)

  return res.status(200).send({message: 'ok'})
}
