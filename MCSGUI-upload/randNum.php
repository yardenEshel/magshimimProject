<?php

if(isset($_POST['function2call']) && !empty($_POST['function2call'])) // if a function was called
{
    $function2call = $_POST['function2call']; //get called function's name
	$randNum = "randNum"; 
    if($function2call == $randNum) //if function "randNum" was called 
	{
        echo (rand(1,2000000000)); //return random number between 1 to 2000000000
    }
}

?>