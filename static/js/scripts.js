/*
$(document).ready(function(){
    console.log('here')
    $('#sign-up-form').on('submit', function(){
        var serializedData = $(this).serialize()
        $.ajax({
            method:'POST',
            url:'/api/register/',
            data: {
                serializedData
              },
              success: function(response) {
                $('#email').val(''),
                $('#first_name').val(''),
                $('#last_name').val(''),
                $('#fbvn').val(''),
                $('#floatingPassword1').val(''),
                $('#floatingPassword2').val(''),
                console.log('success')
                console.log(response.response)
            },
        
            error: function(response) {
                console.log(response)
            },
          });
      });
  });
*/