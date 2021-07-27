$(document).ready(function(){

  $.ajax({
    url: "/getUsername",
    dataType: 'text',
    success: function(data)
    {
        if(data != 'None')
        {
          var headerLinks = $("<div>Welcome, " + data + "</div> <a href=\"/settings\">Settings</a> | <a href=\"/logout\">Sign Out</a>");
          $("#page-header").append(headerLinks);
        }
        else
        {
          var headerLinks = $("<a href=\"/login\">Sign In</a> | <a href=\"/create\">Create Account</a>")
          $("#page-header").append(headerLinks);
        }
    },
    error: function() { alert("Could not load user data.");  }
  });
});