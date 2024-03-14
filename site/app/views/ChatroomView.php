<?php

namespace app\views;

use app\libraries\Core;
use app\libraries\Output;

class ChatroomView extends AbstractView {
    public function __construct(Core $core, Output $output) {
        parent::__construct($core, $output);
        $this->core->getOutput()->addBreadcrumb("Live Lecture Chat", $this->core->buildCourseUrl(['chat']));
        $this->core->getOutput()->addInternalCss('chatroom.css');
        $this->core->getOutput()->addInternalJs('chatroom.js');
        $this->core->getOutput()->addInternalJs('websocket.js');
    }

    public function showChatPageInstructor(array $chatrooms) {
        return $this->core->getOutput()->renderTwigTemplate("chat/ChatPageIns.twig", [
            'csrf_token' => $this->core->getCsrfToken(),
            'base_url' => $this->core->buildCourseUrl() . '/chat',
            'semester' => $this->core->getConfig()->getTerm(),
            'course' => $this->core->getConfig()->getCourse(),
            'chatrooms' => $chatrooms
        ]);
    }

    public function showChatPageStudent(array $chatrooms) {
        return $this->core->getOutput()->renderTwigTemplate("chat/ChatPageStu.twig", [
            'csrf_token' => $this->core->getCsrfToken(),
            'base_url' => $this->core->buildCourseUrl() . '/chat',
            'semester' => $this->core->getConfig()->getTerm(),
            'course' => $this->core->getConfig()->getCourse(),
            'chatrooms' => $chatrooms
        ]);
    }

    public function showAllChatrooms(array $chatrooms) {
        return $this->core->getOutput()->renderTwigTemplate("chat/AllChatroomsPage.twig", [
            'csrf_token' => $this->core->getCsrfToken(),
            'base_url' => $this->core->buildCourseUrl() . '/chat',
            'semester' => $this->core->getConfig()->getTerm(),
            'chatrooms' => $chatrooms,
            'user_admin' => $this->core->getUser()->accessAdmin()
        ]);
    }

    public function showChatroom($chatroom, $anonymous = false) {
        $this->core->getOutput()->addBreadcrumb("Chatroom");
        $user = $this->core->getUser();
        $display_name = $user->getDisplayFullName();
        if (!$anonymous) {
            if (!$user->accessAdmin()) {
                $display_name = $user->getDisplayedGivenName() . " " . substr($user->getDisplayedFamilyName(), 0, 1) . ".";
            }
        }
        else {
            $adjectives = ["Quick", "Lazy", "Cheerful", "Pensive", "Mysterious", "Bright", "Sly", "Brave", "Calm", "Eager", "Fierce", "Gentle", "Jolly", "Kind", "Lively", "Nice", "Proud", "Quiet", "Rapid", "Swift"];
            $anon_names = ["Duck", "Goose", "Swan", "Eagle", "Parrot", "Owl", "Sparrow", "Robin", "Pigeon", "Falcon", "Hawk", "Flamingo", "Pelican", "Seagull", "Cardinal", "Canary", "Finch", "Hummingbird"];
            $display_name = 'Anonymous' . ' ' . $adjectives[array_rand($anon_names)] . ' ' . $anon_names[array_rand($anon_names)];
        }

        return $this->core->getOutput()->renderTwigTemplate("chat/Chatroom.twig", [
            'csrf_token' => $this->core->getCsrfToken(),
            'base_url' => $this->core->buildCourseUrl() . '/chat',
            'semester' => $this->core->getConfig()->getTerm(),
            'course' => $this->core->getConfig()->getCourse(),
            'chatroom' => $chatroom,
            'user_admin' => $this->core->getUser()->accessAdmin(),
            'user_id' => $this->core->getUser()->getId(),
            'user_display_name' => $display_name,
            'anonymous' => $anonymous,
        ]);
    }
}