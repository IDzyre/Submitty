<?php

declare(strict_types=1);

namespace app\entities\chat;

use DateTime;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity]
#[ORM\Table(name: "chatroom_messages")]
class Message {
    #[ORM\Id]
    #[ORM\Column(name: "id", type: Types::INTEGER)]
    #[ORM\GeneratedValue]
    private int $id;

    #[ORM\ManyToOne(targetEntity: Chatroom::class)]
    #[ORM\JoinColumn(name: "chatroom_id", referencedColumnName: "id")]
    private Chatroom $chatroom;

    #[ORM\Column(type: Types::STRING)]
    private string $user_id;

    #[ORM\Column(type: Types::STRING)]
    private string $display_name;

    #[ORM\Column(type: Types::BOOLEAN)]
    private bool $is_pinned;

    #[ORM\Column(type: Types::STRING)]
    private string $who_pinned;

    #[ORM\Column(type: Types::STRING)]
    private string $role;

    #[ORM\Column(type: Types::TEXT)]
    private string $content;

    #[ORM\Column(type: Types::DATETIMETZ_MUTABLE)]
    private DateTime $timestamp;

    public function __construct($userId, $displayName, $role, $text, $chatroom) {
        $this->setUserId($userId);
        $this->setDisplayName($displayName);
        $this->setRole($role);
        $this->setTimestamp(new \DateTime("now"));
        $this->setContent($text);
        $this->setChatroom($chatroom);
        $this->setIsPinned(false);
        $this->setWhoPinned('');
    }

    public function getId(): int {
        return $this->id;
    }

    public function isPinned(): bool {
        return $this->is_pinned;
    }

    public function setIsPinned(bool $is_pinned): void {
        $this->is_pinned = $is_pinned;
    }

    public function getWhoPinned(): string {
        return $this->who_pinned;
    }

    public function setWhoPinned(string $who_pinned): void {
        $this->who_pinned = $who_pinned;
    }

    public function getUserId(): string {
        return $this->user_id;
    }

    public function setUserId($userId): void {
        $this->user_id = $userId;
    }

    public function getDisplayName(): string {
        return $this->display_name;
    }

    public function setDisplayName($displayName): void {
        $this->display_name = $displayName;
    }

    public function getRole(): string {
        return $this->role;
    }

    public function setRole($role): string {
        return $this->role = $role;
    }

    public function getContent(): string {
        return $this->content;
    }

    public function setContent(string $text): void {
        $this->content = $text;
    }

    public function getTimestamp(): DateTime {
        return $this->timestamp;
    }

    public function setTimestamp(DateTime $timestamp): void {
        $this->timestamp = $timestamp;
    }

    public function getChatroom(): Chatroom {
        return $this->chatroom;
    }

    public function setChatroom(Chatroom $chatroom): void {
        $this->chatroom = $chatroom;
    }
}
