import Select from 'react-select'
import chroma from 'chroma-js'

export function ColorMultiSelect({
  colorsMapper,
  options,
  values,
  setValues,
  name = 'modalities',
}) {
  const selectControlStyles = {
    control: styles => ({
      ...styles,
      borderRadius: '0.375rem',
      borderColor: '#E2E8F0',
      minHeight: '40px',
    }),
    option: (styles, {data, isSelected, isFocused}) => {
      const color = chroma(colorsMapper[data.value])
      return {
        ...styles,
        backgroundColor: isFocused ? color.alpha(0.3).css() : undefined,
        color: color.darken().css(),
      }
    },
    multiValue: (styles, {data}) => {
      const color = chroma(colorsMapper[data.value])
      return {
        ...styles,
        backgroundColor: color.alpha(1.0).css(),
      }
    },
  }

  return (
    <Select
      name={name}
      options={options}
      value={values}
      isMulti
      className="basic-multi-select"
      classNamePrefix="select"
      onChange={opts => setValues(opts)}
      styles={selectControlStyles}
    />
  )
}

export default ColorMultiSelect
