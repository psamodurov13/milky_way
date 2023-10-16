const phoneCodes = JSON.parse(document.getElementById('phone_codes').textContent);
  console.log(phoneCodes)

  const forms = document.querySelectorAll('.form-block')
  console.log('Все формы')
  console.log(forms)

  forms.forEach((form) => {
    const countrySelect = form.querySelector('select')
    console.log('Select')
    console.log(countrySelect)

    countrySelect.addEventListener('change', () => {
      console.log('Выбран элемент')
      console.log(countrySelect.value)
      const phoneField = form.querySelector('#div_id_phone input')
      console.log('Field')
      console.log(phoneField)
      phoneCodes.forEach((countryData) => {
        if (countryData.code === countrySelect.value) {
          phoneField.placeholder = countryData.mask
          phoneField.setAttribute('data-phone-pattern', countryData.mask)
        }
      })
    })

  })